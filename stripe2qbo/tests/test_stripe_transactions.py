import os
from dotenv import load_dotenv

import pytest
import stripe

from stripe2qbo.stripe.stripe_transactions import get_transaction

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


@pytest.fixture
def test_customer():
    stripe_customer = stripe.Customer.create(
        email="test@example.com",
        name="Test Customer",
        source="tok_visa",
        stripe_account=ACCOUNT_ID,
    )

    yield stripe_customer

    stripe.Customer.delete(stripe_customer.id, stripe_account=ACCOUNT_ID)


def test_charge_transaction(test_customer):
    test_charge = stripe.Charge.create(
        amount=1000,
        currency="usd",
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
    )
    txn = stripe.BalanceTransaction.list(limit=1, stripe_account=ACCOUNT_ID).data[0]

    transaction = get_transaction(txn.id, ACCOUNT_ID)

    assert transaction.type == "charge"
    if transaction.currency == "usd":
        assert transaction.amount == 1000
    else:
        assert transaction.exchange_rate is not None
        amount = round(1000 * transaction.exchange_rate)
        assert transaction.amount == amount

    assert transaction.customer is not None
    assert transaction.customer.id == test_customer.id
    assert transaction.customer.name == "Test Customer"
    assert transaction.customer.email == "test@example.com"

    assert transaction.charge is not None
    assert transaction.charge.id == test_charge.id
    assert transaction.charge.amount == 1000

    assert transaction.payout is None
    assert transaction.invoice is None


def test_invoice_transaction(test_customer):
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=1000,
        currency="usd",
        description="Test Invoice Item",
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

    assert transaction.type == "charge"
    if transaction.currency == "usd":
        assert transaction.amount == 1000
    else:
        assert transaction.exchange_rate is not None
        amount = round(1000 * transaction.exchange_rate)
        assert transaction.amount == amount

    assert transaction.customer is not None
    assert transaction.customer.id == test_customer.id

    assert transaction.charge is not None
    assert transaction.charge.amount == 1000

    assert transaction.invoice is not None
    assert transaction.invoice.id == test_invoice.id
    assert transaction.invoice.amount_due == 1000

    assert transaction.invoice.lines is not None
    assert len(transaction.invoice.lines) == 1
    line = transaction.invoice.lines[0]
    assert line.amount == 1000
    assert line.description == "Test Invoice Item"


@pytest.mark.skip(reason="TODO: ensure available balance is nonzero")
def test_payout_transaction(test_customer):
    test_payout = stripe.Payout.create(
        amount=1,
        currency="usd",
        stripe_account=ACCOUNT_ID,
    )
    txn = stripe.BalanceTransaction.list(limit=1, stripe_account=ACCOUNT_ID).data[0]

    transaction = get_transaction(txn.id, ACCOUNT_ID)

    assert transaction.type == "payout"
    assert transaction.payout is not None
    assert transaction.payout.id == test_payout.id

    assert transaction.customer is None
    assert transaction.charge is None
    assert transaction.invoice is None
