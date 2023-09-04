import os
from dotenv import load_dotenv
from datetime import datetime

import pytest
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.stripe.stripe_transactions import build_transaction, get_transaction
from stripe2qbo.sync import transfer_from_payout, expense_from_transaction
from stripe2qbo.transforms import qbo_invoice_from_stripe_invoice

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


@pytest.fixture
def test_settings():
    return Settings(
        stripe_clearing_account_id="1",
        stripe_payout_account_id="2",
        stripe_vendor_id="3",
        stripe_fee_account_id="4",
        default_income_account_id="5",
        default_tax_code_id="6",
        exempt_tax_code_id="7",
    )


def test_transfer_from_payout(test_settings):
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


def test_expense_from_transaction(test_customer, test_settings):
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

    expense = expense_from_transaction(transaction, test_settings)

    assert expense is not None
    assert expense.AccountRef.value == test_settings.stripe_clearing_account_id
    assert expense.EntityRef.value == test_settings.stripe_vendor_id
    assert expense.TotalAmt == transaction.fee / 100
    assert expense.TxnDate == datetime.fromtimestamp(transaction.created).strftime(
        "%Y-%m-%d"
    )
    assert (
        expense.PrivateNote
        == f"""
            {transaction.description}
            {transaction.id}
            {test_charge.id}
        """
    )
    assert expense.Line[0].Amount == transaction.fee / 100
    assert (
        expense.Line[0].AccountBasedExpenseLineDetail.AccountRef.value
        == test_settings.stripe_fee_account_id
    )


def test_invoice_transform(test_customer, test_settings):
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
    qbo_invoice = qbo_invoice_from_stripe_invoice(
        stripe_invoice, test_customer.id, test_settings
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
    assert (
        qbo_invoice.Line[1].SalesItemLineDetail.TaxCodeRef.value
        == test_settings.exempt_tax_code_id
    )
    assert qbo_invoice.Line[0].Amount == 5
    assert qbo_invoice.Line[0].SalesItemLineDetail.ItemRef.name == "Product 2"
    assert (
        qbo_invoice.Line[0].SalesItemLineDetail.TaxCodeRef.value
        == test_settings.exempt_tax_code_id
    )

    assert qbo_invoice.TxnTaxDetail is not None
    assert qbo_invoice.TxnTaxDetail.TotalTax == 0
    assert qbo_invoice.TxnTaxDetail.TaxLine is not None
    assert len(qbo_invoice.TxnTaxDetail.TaxLine) == 1
    assert qbo_invoice.TxnTaxDetail.TaxLine[0].Amount == 0
    assert qbo_invoice.TxnTaxDetail.TaxLine[0].TaxLineDetail.NetAmountTaxable == 15
