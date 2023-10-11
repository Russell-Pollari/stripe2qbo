import os
import json
from datetime import datetime

import pytest
import stripe
from dotenv import load_dotenv
from stripe2qbo.api.auth import get_password_hash

from stripe2qbo.qbo.QBO import QBO, create_qbo
from stripe2qbo.db.models import User
from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.auth import (
    Token,
    generate_auth_token,
    refresh_auth_token,
    get_auth_url,
)
from stripe2qbo.stripe.models import Transaction
from stripe2qbo.stripe.stripe_transactions import get_transaction


stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")

load_dotenv()


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


# TODO: monkey patch the redirect env variable?
# TODO: Instructions for setting this up for the first time
@pytest.fixture
def test_token() -> Token:
    """Get a test token QBO token.

    Returns:
        Token: QBO token
    """
    if os.path.exists("test_token.json"):
        with open("test_token.json") as f:
            token = json.load(f)
            token = Token(**token)
            if datetime.fromisoformat(token.expires_at) < datetime.now():
                token = refresh_auth_token(token.refresh_token, token.realm_id)

    else:
        auth_url = get_auth_url()
        print(f"Please visit {auth_url} and fill in the prompts below.")
        code = input("Code: ")
        realm_id = input("Realm ID: ")
        token = generate_auth_token(code, realm_id)

    with open("test_token.json", "w") as f:
        json.dump(token.model_dump(), f)

    return token


@pytest.fixture
def test_user(test_token: Token) -> User:
    pswd = get_password_hash("test")
    user = User(
        id=100,
        email="testuser@test.com",
        hashed_password=pswd,
        qbo_realm_id=test_token.realm_id,
        stripe_user_id=os.getenv("TEST_STRIPE_USER_ID", ""),
    )
    return user


@pytest.fixture
async def test_qbo(test_token: Token) -> QBO:
    qbo = await create_qbo(test_token)
    assert qbo.access_token is not None
    assert qbo.realm_id is not None
    assert qbo.home_currency is not None
    return qbo


@pytest.fixture
async def test_settings(test_qbo: QBO) -> Settings:
    stripe_clearing_account_id = await test_qbo.get_or_create_account(
        "Stripe", "Bank", account_sub_type="Checking"
    )
    stripe_payout_account_id = await test_qbo.get_or_create_account(
        "Stripe Payouts", "Bank", account_sub_type="Checking"
    )
    sync_stripe_fee_account_id = await test_qbo.get_or_create_account(
        "Stripe Fees", "Expense", account_sub_type="OtherBusinessExpenses"
    )
    default_income_account_id = await test_qbo.get_or_create_account(
        "Stripe Income", "Income", account_sub_type="SalesOfProductIncome"
    )
    stripe_vendor_id = await test_qbo.get_or_create_vendor("Stripe")

    # TODO: default tax settings - depending on QBO locale and preferences
    return Settings(
        stripe_clearing_account_id=stripe_clearing_account_id,
        stripe_payout_account_id=stripe_payout_account_id,
        stripe_vendor_id=stripe_vendor_id,
        stripe_fee_account_id=sync_stripe_fee_account_id,
        default_income_account_id=default_income_account_id,
        default_tax_code_id="TAX",
        exempt_tax_code_id="NON",
    )


@pytest.fixture(params=["usd", "cad"])
def test_charge_transaction(
    test_customer: stripe.Customer, request: pytest.FixtureRequest
) -> Transaction:
    stripe.Charge.create(
        amount=1000,
        currency=request.param,
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
    )
    txn = stripe.BalanceTransaction.list(
        limit=1,
        type="charge",
        stripe_account=ACCOUNT_ID,
        expand=["data.source", "data.source.customer"],
    ).data[0]

    transaction = get_transaction(txn.id, ACCOUNT_ID)
    return transaction


@pytest.fixture(params=["usd", "cad"])
def test_invoice_transaction(
    test_customer: stripe.Customer, request: pytest.FixtureRequest
) -> Transaction:
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=1000,
        currency=request.param,
        description="Product A",
        stripe_account=ACCOUNT_ID,
    )
    stripe.InvoiceItem.create(
        customer=test_customer.id,
        amount=500,
        currency=request.param,
        description="Product B",
        stripe_account=ACCOUNT_ID,
    )
    test_invoice = stripe.Invoice.create(
        customer=test_customer.id,
        stripe_account=ACCOUNT_ID,
        collection_method="send_invoice",
        currency=request.param,
        days_until_due=30,
    )
    stripe.Invoice.pay(test_invoice.id, stripe_account=ACCOUNT_ID)
    txn = stripe.BalanceTransaction.list(limit=1, stripe_account=ACCOUNT_ID).data[0]

    transaction = get_transaction(txn.id, ACCOUNT_ID)
    return transaction
