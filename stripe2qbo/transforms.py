from typing import Dict, cast, Optional
import datetime

from stripe2qbo.db.schemas import Settings
import stripe2qbo.qbo.models as qbo_models
import stripe2qbo.stripe.models as stripe_models


def _timestamp_to_date(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def transfer_from_payout(
    payout: stripe_models.Payout, settings: Settings
) -> qbo_models.Transfer:
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


def expense_from_transaction(
    transaction: stripe_models.Transaction,
    settings: Settings,
) -> qbo_models.Expense:
    if transaction.type in ["charge", "payment"]:
        charge = cast(stripe_models.Charge, transaction.charge)
        amount = transaction.fee / 100
        description = f"Stripe fee for charge {charge.id}"
    else:
        amount = -transaction.amount / 100
        description = transaction.description or ""

    currency = cast(qbo_models.QBOCurrency, transaction.currency)
    account_id = settings.stripe_clearing_account_id
    vendor_id = settings.stripe_vendor_id

    return qbo_models.Expense(
        TotalAmt=amount,
        ExchangeRate=transaction.exchange_rate or 1.0,
        CurrencyRef=qbo_models.CurrencyRef(value=currency),
        AccountRef=qbo_models.ItemRef(value=account_id),
        EntityRef=qbo_models.ItemRef(value=vendor_id),
        TxnDate=_timestamp_to_date(transaction.created).strftime("%Y-%m-%d"),
        PrivateNote=f"""
            {description}
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


def qbo_invoice_line_from_stripe_invoice_line(
    line: stripe_models.InvoiceLine,
    settings: Settings,
) -> qbo_models.InvoiceLine:
    if line.tax_amounts:
        tax_code_id = settings.default_tax_code_id
    else:
        tax_code_id = settings.exempt_tax_code_id

    product = qbo_models.ProductItemRef(
        name=line.product.name,
    )

    return qbo_models.InvoiceLine(
        Amount=line.amount / 100,
        Description=line.description,
        SalesItemLineDetail=qbo_models.SalesItemLineDetail(
            ItemRef=product,
            TaxCodeRef=qbo_models.TaxCodeRef(value=tax_code_id),
        ),
    )


def tax_detail_from_invoice(
    invoice: stripe_models.Invoice,
    tax_codes: Dict[str, qbo_models.TaxCode | None],
    settings: Settings,
) -> qbo_models.TaxDetail:
    """Create a QBO TaxDetail from a Stripe Invoice.

    Adding tax codes to InvoiceLines is often sufficient.
    However, to override QBO's calculated tax amounts, this is necessary.
    Useful to ensure Stripe invoice and QBO invoice have same total tax amounts

    Args:
        invoice (Invoice): Stripe invoice
        settings (Settings): Sync Settings object

    Returns:
        qbo.TaxDetail: QBO TaxDetail object
    """
    total_tax = invoice.tax or 0
    total_taxable_amount = 0
    tax_details: Dict[str, qbo_models.TaxLineModel] = {}  # tax_code_id: TaxLineModel

    for line in invoice.lines:
        for tax_amount in line.tax_amounts:
            assert tax_amount.tax_rate is not None
            total_taxable_amount += tax_amount.taxable_amount

            tax_code_id = settings.default_tax_code_id

            if tax_code_id == "TAX" or tax_code_id == "":
                # Don't need TaxLineDetail if using default tax code
                continue

            tax_code = cast(qbo_models.TaxCode, tax_codes[tax_code_id])
            tax_rate_ref = tax_code.SalesTaxRateList.TaxRateDetail[0].TaxRateRef

            detail = tax_details.get(tax_code_id)
            if detail is not None:
                detail.Amount += tax_amount.amount / 100
                detail.TaxLineDetail.NetAmountTaxable += tax_amount.taxable_amount / 100
            else:
                tax_details[tax_code_id] = qbo_models.TaxLineModel(
                    Amount=tax_amount.amount / 100,
                    TaxLineDetail=qbo_models.TaxLineDetail(
                        TaxRateRef=tax_rate_ref,
                        NetAmountTaxable=tax_amount.taxable_amount / 100,
                        TaxPercent=tax_amount.tax_rate.percentage,
                    ),
                )

    untaxed_amount = invoice.amount_due - total_tax - total_taxable_amount

    if (
        untaxed_amount > 0
        and settings.exempt_tax_code_id != "NON"
        and settings.exempt_tax_code_id != ""
    ):
        tax_code_id = settings.exempt_tax_code_id
        tax_code = cast(qbo_models.TaxCode, tax_codes[tax_code_id])
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


def qbo_invoice_from_stripe_invoice(
    invoice: stripe_models.Invoice,
    customer_id: str,
    tax_codes: Dict[str, qbo_models.TaxCode | None],
    settings: Settings,
    exchange_rate: float = 1.0,
) -> qbo_models.Invoice:
    invoice_lines = [
        qbo_invoice_line_from_stripe_invoice_line(
            line,
            settings,
        )
        for line in invoice.lines
    ]

    tax_detail = tax_detail_from_invoice(invoice, tax_codes, settings)

    qbo_invoice = qbo_models.Invoice(
        CustomerRef=qbo_models.ItemRef(value=customer_id),
        CurrencyRef={
            "value": invoice.currency.upper(),  # type: ignore
        },
        ExchangeRate=exchange_rate,
        TxnDate=_timestamp_to_date(invoice.created).strftime("%Y-%m-%d"),
        Line=invoice_lines,
        DocNumber=invoice.number,
        PrivateNote=f"{invoice.number}\n{invoice.id}",
        TxnTaxDetail=tax_detail,
    )

    if invoice.due_date:
        qbo_invoice.DueDate = _timestamp_to_date(invoice.due_date).strftime("%Y-%m-%d")

    return qbo_invoice


def payment_from_charge(
    charge: stripe_models.Charge,
    customer_id: str,
    settings: Settings,
    invoice_id: Optional[str] = None,
    exchange_rate: float = 1.0,
) -> qbo_models.Payment:
    currency = cast(qbo_models.QBOCurrency, charge.currency.upper())

    payment = qbo_models.Payment(
        TotalAmt=charge.amount / 100,
        CurrencyRef=qbo_models.CurrencyRef(value=currency),
        CustomerRef=qbo_models.ItemRef(value=customer_id),
        DepositToAccountRef=qbo_models.ItemRef(
            value=settings.stripe_clearing_account_id
        ),
        TxnDate=_timestamp_to_date(charge.created).strftime("%Y-%m-%d"),
        PrivateNote=f"{charge.description}\n{charge.id}",
        ExchangeRate=cast(float, exchange_rate),
    )

    if invoice_id:
        payment.Line = [
            qbo_models.PaymentLine(
                Amount=payment.TotalAmt,
                LinkedTxn=[qbo_models.LinkedTxn(TxnId=invoice_id)],
            )
        ]

    return payment
