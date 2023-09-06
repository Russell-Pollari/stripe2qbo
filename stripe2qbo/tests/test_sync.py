import os
from datetime import datetime

from dotenv import load_dotenv
import stripe

from stripe2qbo.stripe.stripe_transactions import build_transaction
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.sync import sync_transaction

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


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
