import pytest

from stripe2qbo.api.routers.transaction_router import (
    get_all_transactions,
    get_transaction_by_id,
)
from stripe2qbo.qbo.auth import Token
from stripe2qbo.db.models import TransactionSync, User, QBOToken
from stripe2qbo.db.database import SessionLocal

db = SessionLocal()

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def test_transaction(test_user: User, test_token: Token):
    test_qbo_token = QBOToken(**test_token.model_dump(), user_id=test_user.id)
    db.add(test_qbo_token)
    db.add(test_user)

    transaction_sync1 = TransactionSync(
        id="12281",
        user_id=test_user.id,
        created=123,
        type="charge",
        fee=123,
        currency="cad",
        amount=1000,
        description="Test Charge",
        stripe_id="123",
        status="pending",
    )
    db.add(transaction_sync1)
    db.commit()

    yield

    db.delete(test_user)
    db.delete(test_qbo_token)
    db.delete(transaction_sync1)
    db.commit()


@pytest.mark.asyncio
async def test_get_all_transactions(test_user: User, test_transaction: None):
    test_value = await get_all_transactions(test_user, db)

    assert len(test_value) == 1
    assert test_value[0].user_id == test_user.id
    assert test_value[0].description == "Test Charge"


@pytest.mark.asyncio
async def test_get_transaction_by_id(test_user: User, test_transaction: None):
    test_value = await get_transaction_by_id(test_user, db, "12281")

    assert test_value.user_id == test_user.id
    assert test_value.description == "Test Charge"
