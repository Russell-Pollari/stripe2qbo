import os
from dotenv import load_dotenv
from datetime import datetime

import pytest
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.stripe.stripe_transactions import build_transaction
from stripe2qbo.sync import transfer_from_payout

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
