from typing import Dict
import os
from datetime import datetime

from dotenv import load_dotenv
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.QBO import QBO
from stripe2qbo.qbo.models import TaxCode
from stripe2qbo.stripe.models import Transaction
from stripe2qbo.stripe.stripe_transactions import build_transaction, get_transaction
from stripe2qbo.sync_helpers import (
    payment_from_charge,
    qbo_invoice_from_stripe_invoice,
    transfer_from_payout,
    expense_from_transaction,
)

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


def test_transfer_from_payout(test_settings: Settings):
    txn = stripe.BalanceTransaction.list(
        limit=1, type="payout", stripe_account=ACCOUNT_ID, expand=["data.source"]
    ).data[0]

    transaction = build_transaction(txn, ACCOUNT_ID)
    assert transaction.payout is not None
    transfer = transfer_from_payout(transaction.payout, test_settings)

    assert transfer is not None

    if transaction.amount < 0:
        assert transfer.Amount == -transaction.amount / 100
        assert transfer.FromAccountRef.value == test_settings.stripe_clearing_account_id
        assert transfer.ToAccountRef.value == test_settings.stripe_payout_account_id
    else:
        assert transfer.Amount == transaction.amount / 100
        assert transfer.FromAccountRef.value == test_settings.stripe_payout_account_id
        assert transfer.ToAccountRef.value == test_settings.stripe_clearing_account_id

    assert transfer.TxnDate == datetime.fromtimestamp(transaction.created).strftime(
        "%Y-%m-%d"
    )
    assert (
        transfer.PrivateNote
        == f"{transaction.payout.description}\n{transaction.payout.id}"
    )


def test_expense_from_transaction(
    test_charge_transaction: Transaction, test_settings: Settings
):
    assert test_charge_transaction.charge is not None
    currency = test_charge_transaction.currency.upper()
    expense = expense_from_transaction(
        test_charge_transaction, test_settings
    )  # type: ignore

    assert expense is not None
    assert expense.CurrencyRef.value == currency
    assert expense.AccountRef.value == test_settings.stripe_clearing_account_id
    assert expense.EntityRef.value == test_settings.stripe_vendor_id

    assert expense.TotalAmt == test_charge_transaction.fee / 100
    assert expense.TxnDate == datetime.fromtimestamp(
        test_charge_transaction.created
    ).strftime("%Y-%m-%d")
    assert (
        expense.PrivateNote
        == f"""
            Stripe fee for charge {test_charge_transaction.charge.id}
            {test_charge_transaction.id}
            {test_charge_transaction.charge.id}
        """
    )
    assert expense.Line[0].Amount == test_charge_transaction.fee / 100
    assert (
        expense.Line[0].AccountBasedExpenseLineDetail.AccountRef.value
        == test_settings.stripe_fee_account_id
    )


def test_invoice_transform(test_customer, test_settings: Settings, test_qbo: QBO):
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=1000,
        currency="usd",
        description="Product 1",
        stripe_account=ACCOUNT_ID,
    )
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=500,
        currency="usd",
        description="Product 2",
        stripe_account=ACCOUNT_ID,
    )
    test_invoice = stripe.Invoice.create(
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
        collection_method="send_invoice",
        currency="usd",
        days_until_due=30,
    )
    stripe.Invoice.pay(test_invoice.id, stripe_account=ACCOUNT_ID)
    txn = stripe.BalanceTransaction.list(limit=1, stripe_account=ACCOUNT_ID).data[0]
    transaction = get_transaction(txn.id, ACCOUNT_ID)
    stripe_invoice = transaction.invoice

    assert stripe_invoice is not None
    assert stripe_invoice.due_date is not None

    # TAX and NON will throw an error if queried..
    tax_codes: Dict[str, TaxCode | None] = {}

    tax_codes[test_settings.default_tax_code_id] = (
        test_qbo.get_tax_code(test_settings.default_tax_code_id)
        if test_settings.default_tax_code_id != "TAX"
        else None
    )
    tax_codes[test_settings.exempt_tax_code_id] = (
        test_qbo.get_tax_code(test_settings.exempt_tax_code_id)
        if test_settings.exempt_tax_code_id != "NON"
        else None
    )

    qbo_invoice = qbo_invoice_from_stripe_invoice(
        stripe_invoice, test_customer.id, tax_codes, test_settings
    )

    assert qbo_invoice is not None
    assert qbo_invoice.CustomerRef.value == test_customer.id
    assert qbo_invoice.CurrencyRef.value == "USD"
    assert qbo_invoice.DueDate == datetime.fromtimestamp(
        stripe_invoice.due_date
    ).strftime("%Y-%m-%d")
    assert qbo_invoice.TxnDate == datetime.fromtimestamp(
        stripe_invoice.created
    ).strftime("%Y-%m-%d")
    assert qbo_invoice.PrivateNote == f"{stripe_invoice.number}\n{stripe_invoice.id}"
    assert qbo_invoice.DocNumber == stripe_invoice.number

    assert len(qbo_invoice.Line) == 2
    assert qbo_invoice.Line[1].Amount == 10
    assert qbo_invoice.Line[1].SalesItemLineDetail.ItemRef.name == "Product 1"
    assert qbo_invoice.Line[1].SalesItemLineDetail.TaxCodeRef is not None
    assert (
        qbo_invoice.Line[1].SalesItemLineDetail.TaxCodeRef.value
        == test_settings.exempt_tax_code_id
    )
    assert qbo_invoice.Line[0].Amount == 5
    assert qbo_invoice.Line[0].SalesItemLineDetail.ItemRef.name == "Product 2"
    assert qbo_invoice.Line[0].SalesItemLineDetail.TaxCodeRef is not None
    assert (
        qbo_invoice.Line[0].SalesItemLineDetail.TaxCodeRef.value
        == test_settings.exempt_tax_code_id
    )

    assert qbo_invoice.TxnTaxDetail is not None
    assert qbo_invoice.TxnTaxDetail.TotalTax == 0
    assert qbo_invoice.TxnTaxDetail.TaxLine is not None
    # assert len(qbo_invoice.TxnTaxDetail.TaxLine) == 1
    # assert qbo_invoice.TxnTaxDetail.TaxLine[0].Amount == 0
    # assert qbo_invoice.TxnTaxDetail.TaxLine[0].TaxLineDetail.NetAmountTaxable == 15


def test_invoice_transform_with_tax(
    test_customer, test_settings: Settings, test_qbo: QBO
):
    tax_rate = stripe.TaxRate.create(
        display_name="Test Tax Rate",
        inclusive=False,
        percentage=10,
        stripe_account=ACCOUNT_ID,
    )

    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=1000,
        currency="usd",
        description="Product with tax",
        stripe_account=ACCOUNT_ID,
        tax_rates=[tax_rate.id],
    )
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=500,
        currency="usd",
        description="Product without tax",
        stripe_account=ACCOUNT_ID,
    )
    test_invoice = stripe.Invoice.create(
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
        collection_method="send_invoice",
        currency="usd",
        days_until_due=30,
    )
    stripe.Invoice.pay(test_invoice.id, stripe_account=ACCOUNT_ID)
    txn = stripe.BalanceTransaction.list(limit=1, stripe_account=ACCOUNT_ID).data[0]
    transaction = get_transaction(txn.id, ACCOUNT_ID)
    stripe_invoice = transaction.invoice

    assert stripe_invoice is not None
    assert stripe_invoice.due_date is not None
    assert stripe_invoice.tax is not None

    # TAX and NON will throw an error if queried..
    tax_codes: Dict[str, TaxCode | None] = {}

    tax_codes[test_settings.default_tax_code_id] = (
        test_qbo.get_tax_code(test_settings.default_tax_code_id)
        if test_settings.default_tax_code_id != "TAX"
        else None
    )
    tax_codes[test_settings.exempt_tax_code_id] = (
        test_qbo.get_tax_code(test_settings.exempt_tax_code_id)
        if test_settings.exempt_tax_code_id != "NON"
        else None
    )

    qbo_invoice = qbo_invoice_from_stripe_invoice(
        stripe_invoice, test_customer.id, tax_codes, test_settings
    )

    assert len(qbo_invoice.Line) == 2
    assert qbo_invoice.Line[1].Amount == 10
    assert qbo_invoice.Line[1].SalesItemLineDetail.ItemRef.name == "Product with tax"
    assert qbo_invoice.Line[1].SalesItemLineDetail.TaxCodeRef is not None
    assert (
        qbo_invoice.Line[1].SalesItemLineDetail.TaxCodeRef.value
        == test_settings.default_tax_code_id
    )
    assert qbo_invoice.Line[0].Amount == 5
    assert qbo_invoice.Line[0].SalesItemLineDetail.ItemRef.name == "Product without tax"
    assert qbo_invoice.Line[0].SalesItemLineDetail.TaxCodeRef is not None
    assert (
        qbo_invoice.Line[0].SalesItemLineDetail.TaxCodeRef.value
        == test_settings.exempt_tax_code_id
    )

    assert qbo_invoice.TxnTaxDetail is not None
    assert qbo_invoice.TxnTaxDetail.TotalTax == 1
    # assert qbo_invoice.TxnTaxDetail.TaxLine is not None
    # assert len(qbo_invoice.TxnTaxDetail.TaxLine) == 2
    # assert qbo_invoice.TxnTaxDetail.TaxLine[0].Amount == stripe_invoice.tax / 100
    # assert qbo_invoice.TxnTaxDetail.TaxLine[0].Amount == 1
    # assert qbo_invoice.TxnTaxDetail.TaxLine[0].TaxLineDetail.NetAmountTaxable == 10

    # assert qbo_invoice.TxnTaxDetail.TaxLine[1].Amount == 0
    # assert qbo_invoice.TxnTaxDetail.TaxLine[1].TaxLineDetail.NetAmountTaxable == 5


def test_payment_from_charge(test_customer, test_settings):
    test_charge = stripe.Charge.create(
        amount=1000,
        currency="usd",
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
    )

    txn = stripe.BalanceTransaction.list(
        limit=1,
        type="charge",
        stripe_account=ACCOUNT_ID,
        expand=["data.source", "data.source.customer"],
    ).data[0]

    transaction = build_transaction(txn, ACCOUNT_ID)

    assert transaction.charge is not None
    assert transaction.charge.id == test_charge.id
    assert transaction.customer is not None

    payment = payment_from_charge(
        transaction.charge,
        test_customer.id,
        test_settings,
        exchange_rate=transaction.exchange_rate,
    )

    assert payment is not None
    assert payment.CustomerRef.value == test_customer.id
    assert payment.CurrencyRef.value == "USD"
    assert payment.TotalAmt == 10
    assert payment.TxnDate == datetime.fromtimestamp(
        transaction.charge.created
    ).strftime("%Y-%m-%d")
    assert (
        payment.PrivateNote
        == f"{transaction.charge.description}\n{transaction.charge.id}"
    )
    assert payment.DepositToAccountRef.value == test_settings.stripe_clearing_account_id
    assert payment.ExchangeRate == transaction.exchange_rate

    assert payment.Line is None
