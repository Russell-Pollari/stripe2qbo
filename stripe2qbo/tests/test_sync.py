import os
import json
from datetime import datetime

from dotenv import load_dotenv
import pytest
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.auth import get_auth_url, generate_auth_token, refresh_auth_token
from stripe2qbo.stripe.stripe_transactions import build_transaction
from stripe2qbo.qbo.auth import Token
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.sync import sync_transaction

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


@pytest.fixture
def test_settings():
    return Settings(
        stripe_clearing_account_id="100",
        stripe_payout_account_id="35",
        stripe_vendor_id="64",
        stripe_fee_account_id="92",
        default_income_account_id="95",
        default_tax_code_id="TAX",
        exempt_tax_code_id="NON",
    )


# TODO: monkey patch the redirect env variable
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


def test_qbo_token(test_token):
    """Test that the QBO token is valid."""
    assert test_token.access_token is not None
    assert test_token.refresh_token is not None
    assert test_token.expires_at is not None
    assert test_token.refresh_token_expires_at is not None
    assert test_token.realm_id is not None


def test_qbo_request(test_token):
    response = qbo_request(
        path=f"/companyinfo/{test_token.realm_id}",
        access_token=test_token.access_token,
        realm_id=test_token.realm_id,
    )

    assert response.status_code == 200
    assert response.json()["CompanyInfo"]["CompanyName"] is not None
    assert response.json()["CompanyInfo"]["Country"] is not None


def test_sync_payout(test_token, test_settings):
    txn = stripe.BalanceTransaction.list(
        limit=1, type="payout", stripe_account=ACCOUNT_ID, expand=["data.source"]
    ).data[0]

    transaction = build_transaction(txn, ACCOUNT_ID)
    assert transaction.payout is not None

    sync = sync_transaction(transaction, test_settings, test_token)
    assert sync.status == "success"
    assert sync.transfer_id is not None
    assert sync.id == transaction.id

    response = qbo_request(
        path=f"/transfer/{sync.transfer_id}",
        access_token=test_token.access_token,
        realm_id=test_token.realm_id,
    )

    assert response.status_code == 200
    assert response.json()["Transfer"]["Id"] == sync.transfer_id
    assert response.json()["Transfer"]["TxnDate"] == datetime.fromtimestamp(
        transaction.created
    ).strftime("%Y-%m-%d")
    assert (
        response.json()["Transfer"]["PrivateNote"]
        == f"{transaction.payout.description}\n{transaction.payout.id}"
    )

    if transaction.payout.amount > 0:
        assert response.json()["Transfer"]["Amount"] == transaction.payout.amount / 100
        assert (
            response.json()["Transfer"]["FromAccountRef"]["value"]
            == test_settings.stripe_clearing_account_id
        )
        assert (
            response.json()["Transfer"]["ToAccountRef"]["value"]
            == test_settings.stripe_payout_account_id
        )
    else:
        assert response.json()["Transfer"]["Amount"] == -transaction.payout.amount / 100
        assert (
            response.json()["Transfer"]["FromAccountRef"]["value"]
            == test_settings.stripe_payout_account_id
        )
        assert (
            response.json()["Transfer"]["ToAccountRef"]["value"]
            == test_settings.stripe_clearing_account_id
        )
