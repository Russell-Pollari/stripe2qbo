import os
from datetime import datetime

import pytest
from dotenv import load_dotenv
import stripe

from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.QBO import QBO
from stripe2qbo.qbo.auth import Token
from stripe2qbo.stripe.stripe_transactions import build_transaction
from stripe2qbo.stripe.models import Transaction
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.db.models import User
from stripe2qbo.Stripe2QBO import create_stripe2qbo

load_dotenv()

stripe.api_key = os.getenv("TEST_STRIPE_API_KEY", "")
ACCOUNT_ID = os.getenv("TEST_STRIPE_ACCOUNT_ID", "")


@pytest.mark.skip(
    reason="Esure that the test Stripe account has a payout or available balance"
)
async def test_sync_payout(test_token: Token, test_user: User, test_settings: Settings):
    txn = stripe.BalanceTransaction.list(
        limit=1, type="payout", stripe_account=ACCOUNT_ID, expand=["data.source"]
    ).data[0]

    transaction = build_transaction(txn, ACCOUNT_ID)
    assert transaction.payout is not None

    syncer = await create_stripe2qbo(test_settings, test_token)
    sync = await syncer.sync(transaction, test_user)

    assert sync.status == "success"
    assert sync.transfer_id is not None
    assert sync.id == transaction.id

    response = await qbo_request(
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


async def test_sync_invoice(
    test_token: Token,
    test_settings: Settings,
    test_invoice_transaction: Transaction,
    test_user: User,
    test_qbo: QBO,
):
    transaction = test_invoice_transaction
    assert transaction.invoice is not None
    assert transaction.invoice.due_date is not None
    assert transaction.charge is not None
    assert transaction.customer is not None
    invoice_currency = transaction.invoice.currency.upper()

    syncer = await create_stripe2qbo(test_settings, test_token)
    sync = await syncer.sync(transaction, test_user)

    assert sync.status == "success"
    assert sync.id == transaction.id
    assert sync.invoice_id is not None
    assert sync.payment_id is not None
    assert sync.expense_id is not None

    response = await qbo_request(
        path=f"/invoice/{sync.invoice_id}",
        access_token=test_token.access_token,
        realm_id=test_token.realm_id,
    )
    assert response.status_code == 200

    invoice = response.json()["Invoice"]
    assert invoice is not None
    assert invoice["Id"] == sync.invoice_id
    assert invoice["TxnDate"] == datetime.fromtimestamp(transaction.created).strftime(
        "%Y-%m-%d"
    )
    assert invoice["DueDate"] == datetime.fromtimestamp(
        transaction.invoice.due_date
    ).strftime("%Y-%m-%d")
    assert (
        invoice["PrivateNote"]
        == f"{transaction.invoice.number}\n{transaction.invoice.id}"
    )
    assert invoice["CustomerRef"]["name"] in [
        transaction.customer.name,
        f"{transaction.customer.name} ({invoice_currency})",
    ]
    assert invoice["TotalAmt"] == transaction.invoice.amount_due / 100
    assert invoice["CurrencyRef"]["value"] == invoice_currency
    assert invoice["DocNumber"] == transaction.invoice.number
    assert len(invoice["Line"]) == len(transaction.invoice.lines) + 1
    assert invoice["Line"][0]["Amount"] == 5
    assert invoice["Line"][0]["SalesItemLineDetail"]["ItemRef"]["name"] == "Product B"
    assert invoice["Line"][1]["Amount"] == 10
    assert invoice["Line"][1]["SalesItemLineDetail"]["ItemRef"]["name"] == "Product A"

    await test_qbo.set_token(test_token)

    if test_qbo.using_sales_tax:
        assert invoice["TxnTaxDetail"]["TotalTax"] == 0

    response = await qbo_request(
        path=f"/payment/{sync.payment_id}",
        access_token=test_token.access_token,
        realm_id=test_token.realm_id,
    )

    assert response.status_code == 200
    payment = response.json()["Payment"]
    assert payment is not None
    assert payment["Id"] == sync.payment_id
    assert payment["TxnDate"] == datetime.fromtimestamp(
        transaction.charge.created
    ).strftime("%Y-%m-%d")
    assert (
        payment["PrivateNote"]
        == f"{transaction.charge.description}\n{transaction.charge.id}"
    )
    assert payment["CustomerRef"]["name"] in [
        transaction.customer.name,
        f"{transaction.customer.name} ({invoice_currency})",
    ]
    assert payment["TotalAmt"] == transaction.charge.amount / 100
    assert payment["CurrencyRef"]["value"] == invoice_currency
    assert (
        payment["DepositToAccountRef"]["value"]
        == test_settings.stripe_clearing_account_id
    )
    assert payment["Line"][0]["Amount"] == transaction.charge.amount / 100
    assert payment["Line"][0]["LinkedTxn"][0]["TxnId"] == sync.invoice_id

    response = await qbo_request(
        path=f"/purchase/{sync.expense_id}",
        access_token=test_token.access_token,
        realm_id=test_token.realm_id,
    )

    assert response.status_code == 200
    expense = response.json()["Purchase"]
    assert expense is not None
    assert expense["Id"] == sync.expense_id
    assert expense["TxnDate"] == datetime.fromtimestamp(
        transaction.charge.created
    ).strftime("%Y-%m-%d")
    assert f"Stripe fee for charge {transaction.charge.id}" in expense["PrivateNote"]

    assert expense["AccountRef"]["value"] == test_settings.stripe_clearing_account_id
    assert expense["EntityRef"]["value"] == test_settings.stripe_vendor_id
    assert expense["TotalAmt"] == transaction.fee / 100
    assert expense["CurrencyRef"]["value"] == transaction.currency.upper()
    assert expense["Line"][0]["Amount"] == transaction.fee / 100
    assert (
        expense["Line"][0]["AccountBasedExpenseLineDetail"]["AccountRef"]["value"]
        == test_settings.stripe_fee_account_id
    )
