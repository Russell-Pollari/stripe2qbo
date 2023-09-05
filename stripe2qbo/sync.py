from typing import Literal, Optional, Dict
import datetime

from pydantic import BaseModel
from stripe2qbo.qbo.auth import Token

from stripe2qbo.qbo.QBO import QBO
import stripe2qbo.qbo.models as qbo_models
from stripe2qbo.stripe.models import Payout
from stripe2qbo.stripe.stripe_transactions import (
    Transaction,
    Invoice,
)
from stripe2qbo.db.schemas import Settings


class TransactionSync(BaseModel):
    id: str
    created: int
    type: str
    amount: int
    description: str
    status: Optional[Literal["pending", "success", "failed"]] = None


qbo = QBO()


def _timestamp_to_date(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def tax_detail_from_invoice(
    invoice: Invoice, settings: Settings
) -> qbo_models.TaxDetail:
    """Create a QBO TaxDetail from a Stripe Invoice.
    This isn't required. Adding Tax codes to the InvoiceLines is usually sufficient.
    However, if you want to override QBO's calculated tax amounts, this is necessary.
    Useful to ensure Stripe invoice and QBO invoice have same total tax amounts

    Args:
        invoice (Invoice): Stripe invoice

    Returns:
        qbo.TaxDetail: QBO TaxDetail object
    """
    assert invoice.lines is not None  # TODO: enforce this in Invoice model

    tax_details: Dict[str, qbo_models.TaxLineModel] = {}
    total_tax = invoice.tax or 0
    total_taxable_amount = 0
    for line in invoice.lines:
        for tax_amount in line.tax_amounts:
            assert tax_amount.tax_rate is not None
            total_taxable_amount += tax_amount.taxable_amount

            # TODO: custom settings for stripe tax rates
            # stripe_tax_rate_id = tax_amount.tax_rate.id

            tax_code_id = settings.default_tax_code_id
            if tax_code_id == "TAX":
                # No rates associated with this psuedo tax code.
                # The expected TaxDetail object only requires TotalTax
                # TODO: seperate tax logic for US and non US locales
                continue

            tax_code = qbo.get_tax_code(tax_code_id)

            if tax_code is None:
                raise Exception(f"Tax code {tax_code_id} not found")

            tax_rate_ref = tax_code.SalesTaxRateList.TaxRateDetail[0].TaxRateRef

            detail = tax_details.get(tax_code_id)
            if detail is None:
                tax_details[tax_code_id] = qbo_models.TaxLineModel(
                    Amount=tax_amount.amount / 100,
                    TaxLineDetail=qbo_models.TaxLineDetail(
                        TaxRateRef=tax_rate_ref,
                        NetAmountTaxable=tax_amount.taxable_amount / 100,
                        TaxPercent=tax_amount.tax_rate.percentage,
                    ),
                )
            else:
                detail.Amount += tax_amount.amount / 100
                detail.TaxLineDetail.NetAmountTaxable += tax_amount.taxable_amount / 100

    untaxed_amount = invoice.amount_due - total_tax - total_taxable_amount

    if untaxed_amount > 0:
        tax_code_id = settings.exempt_tax_code_id
        if tax_code_id != "NON":
            # No rates associated with the NON psuedo tax code.
            tax_code = qbo.get_tax_code(tax_code_id)
            if tax_code is None:
                raise Exception(f"Tax code {tax_code_id} not found")

            tax_rate_ref = tax_code.SalesTaxRateList.TaxRateDetail[0].TaxRateRef
            tax_details[tax_code_id] = qbo_models.TaxLineModel(
                Amount=0,
                TaxLineDetail=qbo_models.TaxLineDetail(
                    TaxRateRef=tax_rate_ref,
                    NetAmountTaxable=(untaxed_amount) / 100,
                    TaxPercent=0,
                ),
            )

    return qbo_models.TaxDetail(
        TaxLine=list(tax_details.values()),
        TotalTax=total_tax / 100,
    )


def get_income_account_for_product(product_name: str, settings: Settings) -> str:
    """Get or create a QBO income account for a Stripe product product_name.
    If matching product settings are found, use product_setting.qbo_income_account_name.
    If no project settings is found, use settings.QBO_DEFAULT_INCOME_ACCOUNT_NAME
    If QBO_DEFAULT_INCOME_ACCOUNT_NAME is None, use product_name.

    Args:
        product_name (str): Stripe product name

    Returns:
        str: QBO income account name
    """
    # TODO: product settings
    # product_settings = []  # settings.product_settings
    # product_setting = next(
    #     (prod for prod in product_settings if prod.product_name == product_name),
    #     None,
    # )
    # if product_setting is None:
    #     qbo_income_account_id = settings.default_income_account_id
    # else:
    #     income_account_name = (
    #         product_setting.income_account_name
    #         if product_setting.income_account_name
    #         else product_name
    #     )
    #     qbo_income_account_id = qbo.get_or_create_account(income_account_name,
    #                                                           "Income")

    # If no product settings, and no default, use the product name for an income account
    qbo_income_account_id = settings.default_income_account_id
    if qbo_income_account_id is None:
        qbo_income_account_id = qbo.get_or_create_account(product_name, "Income")

    return qbo_income_account_id


def check_for_existing(
    object_type: str,
    qbo_customer_id: Optional[str] = None,
    date: Optional[datetime.datetime] = None,
    private_note: Optional[str] = None,
) -> Optional[str]:
    """Query QBO for an object of type object_type.

    Returns:
        str: QBO object id if found, else None"""
    filter_string = ""
    filters = []

    if date is not None:
        date_string = date.strftime("%Y-%m-%d")
        filters.append(f"TxnDate = '{date_string}'")
    if qbo_customer_id is not None:
        filters.append(f"CustomerRef = '{qbo_customer_id}'")

    if len(filters) > 0:
        filter_string = "where " + " and ".join(filters)

    response = qbo._query(f"select * from {object_type} {filter_string}")
    qbo_items = response.json()["QueryResponse"].get(object_type, [])

    # Cannot query by PrivateNote, so we filter the returned items
    if private_note is not None:
        qbo_items = [
            item for item in qbo_items if private_note in item.get("PrivateNote", "")
        ]

    if len(qbo_items) == 0:
        return None

    return qbo_items[0]["Id"]


def sync_invoice(
    invoice: Invoice,
    qbo_customer_id: str,
    description: Optional[str] = None,
    settings: Optional[Settings] = None,
) -> str:
    """Sync a Stripe invoice to QBO."""
    assert settings is not None
    assert invoice.lines is not None

    qbo_invoice_id = check_for_existing(
        "Invoice",
        qbo_customer_id=qbo_customer_id,
        date=_timestamp_to_date(invoice.created),
        private_note=invoice.id,
    )
    if qbo_invoice_id is not None:
        print(f"Invoice {invoice.id} already synced")  # TODO configurable logging
        return qbo_invoice_id

    invoice_lines = []
    for line in invoice.lines:
        qbo_account_id = get_income_account_for_product(line.product.name, settings)
        qbo_item = qbo.get_or_create_item(line.product.name, qbo_account_id)
        # TODO: customize QBO item with product settings

        # TODO: override with specific tax settings, similar to product logic
        tax_code_id = settings.exempt_tax_code_id
        if line.tax_amounts:
            tax_code_id = settings.default_tax_code_id

        invoice_line = qbo_models.InvoiceLine(
            Description=line.description,
            Amount=line.amount / 100,
            SalesItemLineDetail=qbo_models.SalesItemLineDetail(
                ItemRef=qbo_item,
                TaxCodeRef=qbo_models.TaxCodeRef(value=tax_code_id)
                if tax_code_id
                else None,
            ),
        )
        invoice_lines.append(invoice_line)

    tax_detail = tax_detail_from_invoice(invoice, settings)

    print(f"Creating invoice for {invoice.id}")
    invoice_id = qbo.create_invoice(
        qbo_customer_id,
        invoice_lines,
        created_date=_timestamp_to_date(invoice.created),
        due_date=_timestamp_to_date(invoice.due_date) if invoice.due_date else None,
        currency=invoice.currency.upper(),  # type: ignore
        private_note=f"{description}\n{invoice.id}",
        tax_detail=tax_detail,
        inv_number=invoice.number,
    )

    print(f"Created invoice {invoice_id} for {invoice.id}")

    return invoice_id


def sync_invoice_payment(
    qbo_customer_id: str,
    qbo_invoice_id: Optional[str],
    transaction: Transaction,
    settings: Settings,
) -> str:
    assert transaction.charge is not None

    qbo_payment_id = check_for_existing(
        "Payment",
        qbo_customer_id,
        _timestamp_to_date(transaction.charge.created),
        transaction.charge.id,
    )

    if qbo_payment_id is not None:
        print(f"Payment {transaction.charge.id} already synced")
        return qbo_payment_id

    qbo_stripe_bank_account_id = settings.stripe_clearing_account_id

    payment_id = qbo.create_invoice_payment(
        qbo_invoice_id,
        qbo_customer_id,
        transaction.charge.amount / 100,
        _timestamp_to_date(transaction.charge.created),
        qbo_stripe_bank_account_id,
        transaction.currency.upper(),  # type: ignore
        transaction.exchange_rate,
        private_note=f"{transaction.description}\n{transaction.charge.id}",
    )
    print(f"Created payment {payment_id} for {transaction.charge.id}")
    return payment_id


def expense_from_transaction(
    transaction: Transaction, settings: Settings
) -> qbo_models.Expense:
    if transaction.type in ["charge", "payment"]:
        amount = transaction.fee / 100
    else:
        amount = -transaction.amount / 100

    return qbo_models.Expense(
        TotalAmt=amount,
        AccountRef=qbo_models.ItemRef(value=settings.stripe_clearing_account_id),
        EntityRef=qbo_models.ItemRef(value=settings.stripe_vendor_id),
        TxnDate=_timestamp_to_date(transaction.created).strftime("%Y-%m-%d"),
        PrivateNote=f"""
            {transaction.description}
            {transaction.id}
            {transaction.charge.id if transaction.charge else None}
        """,
        Line=[
            qbo_models.ExpenseLine(
                Amount=amount,
                AccountBasedExpenseLineDetail=qbo_models.AccountBasedExpenseLineDetail(
                    AccountRef=qbo_models.ItemRef(value=settings.stripe_fee_account_id),
                ),
                Description=transaction.description,
            )
        ],
    )


def sync_stripe_fee(transaction: Transaction, settings: Settings) -> str:
    expense_id = check_for_existing(
        "Purchase",
        None,
        _timestamp_to_date(transaction.created),
        transaction.charge.id if transaction.charge else transaction.id,
    )

    if expense_id is not None:
        print(f"Expense for {transaction.id} already synced")
        return expense_id

    expense = expense_from_transaction(transaction, settings)
    expense_id = qbo.create_expense(expense)

    print(f"Created expense {expense_id} for stripe fee {transaction.id}")
    return expense_id


def transfer_from_payout(payout: Payout, settings: Settings) -> qbo_models.Transfer:
    if payout.amount > 0:
        amount = payout.amount
        to_account = settings.stripe_payout_account_id
        from_account = settings.stripe_clearing_account_id
    else:
        amount = payout.amount * -1
        to_account = settings.stripe_clearing_account_id
        from_account = settings.stripe_payout_account_id

    return qbo_models.Transfer(
        Amount=amount / 100,
        FromAccountRef=qbo_models.ItemRef(value=from_account),
        ToAccountRef=qbo_models.ItemRef(value=to_account),
        # TODO: use arrival date?
        TxnDate=_timestamp_to_date(payout.created).strftime("%Y-%m-%d"),
        PrivateNote=f"{payout.description}\n{payout.id}",
    )


def sync_payout(payout: Payout, settings: Settings) -> str:
    transfer_id = check_for_existing("Transfer", private_note=payout.id)
    if transfer_id is not None:
        print(f"Payout {payout.id} already synced")
        return transfer_id

    transfer = transfer_from_payout(payout, settings)
    transfer_id = qbo.create_transfer(transfer)

    print(f"Created transfer {transfer_id} for {payout.id}")
    return transfer_id


def sync_transaction(
    transaction: Transaction, settings: Settings, qbo_token: Token
) -> TransactionSync:
    qbo.set_token(qbo_token)

    sync_status = TransactionSync(
        **transaction.model_dump(),
        status="success",
    )
    if transaction.type == "stripe_fee":
        sync_stripe_fee(transaction, settings)
    elif transaction.type in ["charge", "payment"]:
        assert transaction.charge is not None

        currency: qbo_models.QBOCurrency = transaction.currency.upper()  # type: ignore

        if transaction.customer is not None:
            qbo_customer = qbo.get_or_create_customer(
                transaction.customer.name
                or transaction.customer.description
                or transaction.customer.email,  # type: ignore
                currency,
            )
        else:
            qbo_customer = qbo.get_or_create_customer("STRIPE CUSTOMER", currency)

        if transaction.invoice is None:
            qbo_invoice_id = None
        else:
            qbo_invoice_id = sync_invoice(
                transaction.invoice,
                qbo_customer.Id,
                description=transaction.description,
                settings=settings,
            )

        sync_invoice_payment(qbo_customer.Id, qbo_invoice_id, transaction, settings)

        sync_stripe_fee(transaction, settings)
    elif transaction.type == "payout":
        assert transaction.payout is not None
        sync_payout(transaction.payout, settings)
    else:
        sync_status.status = "failed"

    return sync_status
