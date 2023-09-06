import os
import json
from datetime import datetime

import pytest
import stripe
from dotenv import load_dotenv

from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.auth import (
    Token,
    generate_auth_token,
    refresh_auth_token,
    get_auth_url,
)

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


# TODO: setting this up correctly for a new test account?
@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        stripe_clearing_account_id="100",
        stripe_payout_account_id="35",
        stripe_vendor_id="64",
        stripe_fee_account_id="92",
        default_income_account_id="95",
        default_tax_code_id="TAX",
        exempt_tax_code_id="NON",
    )
