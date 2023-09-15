import pytest

from stripe2qbo.api.routers.transaction_router import (
    get_all_transactions,
    get_transaction_by_id,
)

from stripe2qbo.db.models import TransactionSync, User, QBOToken
from stripe2qbo.db.database import SessionLocal

db = SessionLocal()

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="module")
def test_user():
    test_qbo_token = QBOToken(
        realm_id="8548211",
        access_token="123",
        refresh_token="123",
        expires_at="123",
        refresh_token_expires_at="123",
        user_id=3182831,
    )
    db.add(test_qbo_token)
    db.commit()
    db.refresh(test_qbo_token)

    test_user = User(
        id=3182831,
        qbo_realm_id="8548211",
        stripe_user_id="1234",
        qbo_token=test_qbo_token,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    transaction_sync1 = TransactionSync(
        id="12281",
        user_id=3182831,
        created=123,
        type="charge",
        fee=123,
        currency="cad",
        amount=1000,
        description="Test Charge",
        stripe_id="123",
        qbo_account_id="123",
        status="pending",
        transfer_id="123",
        invoice_id="123",
        payment_id="123",
        expense_id="123",
    )
    db.add(transaction_sync1)
    db.commit()

    yield test_user

    # Finalizer to clean up the user
    db.delete(test_user)
    db.delete(test_qbo_token)
    # # # Finalizer to clean up transaction_syncs
    db.delete(transaction_sync1)
    db.commit()


@pytest.mark.asyncio
async def test_get_all_transactions(test_user):
    test_value = await get_all_transactions(test_user, db)

    assert len(test_value) == 1
    assert test_value[0].user_id == 3182831
    assert test_value[0].description == "Test Charge"


@pytest.mark.asyncio
async def test_get_transaction_by_id(test_user):
    test_value = await get_transaction_by_id(test_user, db, "12281")

    assert test_value.user_id == 3182831
    assert test_value.description == "Test Charge"
