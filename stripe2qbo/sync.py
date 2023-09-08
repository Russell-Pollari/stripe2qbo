from typing import Literal, Optional, Dict, cast
import datetime

from pydantic import BaseModel

from stripe2qbo.qbo.auth import Token
from stripe2qbo.qbo.QBO import QBO
import stripe2qbo.qbo.models as qbo_models
from stripe2qbo.stripe.models import Payout, Transaction, Invoice
from stripe2qbo.db.schemas import Settings
from stripe2qbo.transforms import (
    payment_from_charge,
    qbo_invoice_from_stripe_invoice,
    transfer_from_payout,
    expense_from_transaction,
)


class TransactionSync(BaseModel):
    id: str
    created: int
    type: str
    amount: int
    description: Optional[str] = None
    status: Optional[Literal["pending", "success", "failed"]] = None
    # QBO ids
    transfer_id: Optional[str] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    expense_id: Optional[str] = None


qbo = QBO()


def _timestamp_to_date(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


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
    qbo_income_account_id = None  # settings.default_income_account_id
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
    settings: Settings,
) -> str:
    """Sync a Stripe invoice to QBO."""
    qbo_invoice_id = check_for_existing(
        "Invoice",
        qbo_customer_id=qbo_customer_id,
        date=_timestamp_to_date(invoice.created),
        private_note=invoice.id,
    )
    if qbo_invoice_id is not None:
        print(f"Invoice {invoice.id} already synced")  # TODO configurable logging
        return qbo_invoice_id

    tax_codes: Dict[str, qbo_models.TaxCode | None] = {}

    # TAX and NON will throw an error if queried..
    tax_codes[settings.default_tax_code_id] = (
        qbo.get_tax_code(settings.default_tax_code_id)
        if settings.default_tax_code_id != "TAX"
        else None
    )
    tax_codes[settings.exempt_tax_code_id] = (
        qbo.get_tax_code(settings.exempt_tax_code_id)
        if settings.exempt_tax_code_id != "NON"
        else None
    )

    qbo_invoice = qbo_invoice_from_stripe_invoice(
        invoice, qbo_customer_id, tax_codes, settings
    )

    for line in qbo_invoice.Line:
        product = line.SalesItemLineDetail.ItemRef
        if product.value is None and product.name is not None:
            income_account_id = qbo.get_or_create_account(product.name, "Income")
            line.SalesItemLineDetail.ItemRef = cast(
                qbo_models.ProductItemRef,
                qbo.get_or_create_item(product.name, income_account_id),
            )

    qbo_invoice_id = qbo.create_invoice(qbo_invoice)

    print(f"Created invoice {qbo_invoice_id} for {invoice.id}")
    return qbo_invoice_id


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

    payment = payment_from_charge(
        transaction.charge,
        qbo_customer_id,
        settings,
        exchange_rate=transaction.exchange_rate or 1.0,
        invoice_id=qbo_invoice_id,
    )
    payment_id = qbo.create_payment(payment)
    print(f"Created payment {payment_id} for {transaction.charge.id}")
    return payment_id


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

    currency = transaction.currency.upper()
    if qbo.home_currency != currency:
        date = _timestamp_to_date(transaction.created).strftime("%Y-%m-%d")
        exchange_rate = qbo._request(
            path=f"/exchangerate?sourcecurrencycode={currency}&asofdate={date}"
        ).json()["ExchangeRate"]["Rate"]
    else:
        exchange_rate = 1.0

    expense = expense_from_transaction(transaction, settings, exchange_rate)
    expense_id = qbo.create_expense(expense)

    print(f"Created expense {expense_id} for stripe fee {transaction.id}")
    return expense_id


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
        expense_id = sync_stripe_fee(transaction, settings)
        sync_status.expense_id = expense_id
    elif transaction.type in ["charge", "payment"]:
        assert transaction.charge is not None

        currency = cast(qbo_models.QBOCurrency, transaction.charge.currency.upper())

        if transaction.customer is not None:
            qbo_customer = qbo.get_or_create_customer(
                cast(str, transaction.customer.name or transaction.customer.id),
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
                settings=settings,
            )
            sync_status.invoice_id = qbo_invoice_id

        payment_id = sync_invoice_payment(
            qbo_customer.Id, qbo_invoice_id, transaction, settings
        )
        sync_status.payment_id = payment_id

        expense_id = sync_stripe_fee(transaction, settings)
        sync_status.expense_id = expense_id
    elif transaction.type == "payout":
        assert transaction.payout is not None
        transfer_id = sync_payout(transaction.payout, settings)
        sync_status.transfer_id = transfer_id
    else:
        sync_status.status = "failed"

    return sync_status
