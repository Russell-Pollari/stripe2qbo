import pytest

from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import Depends

from stripe2qbo.api.dependencies import get_current_user, get_db
from stripe2qbo.api.routers.transaction_router import (
    get_all_transactions,
    get_transaction_by_id,
)
from stripe2qbo.db.models import TransactionSync, User, QBOToken

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture
def create_user():
    test_qbo_token = QBOToken(
        realm_id="123",
        access_token="123",
        refresh_token="123",
        expires_at="123",
        refresh_token_expires_at="123",
        user_id=1,
    )
    test_qbo_token.save()

    test_user = User(
        id=1, qbo_realm_id="123", stripe_user_id="1234", qbo_token=test_qbo_token
    )

    test_user.save()


def create_transactionSyncs():
    transaction_sync1 = TransactionSync(
        id="123",
        created=123,
        type="charge",
        amount=1000,
        description="Test Charge",
        stripe_id="123",
        qbo_account_id="123",
        status="pending",
    )
    transaction_sync2 = TransactionSync(
        id="456",
        created=456,
        type="charge",
        amount=1000,
        description="Test Charge",
        stripe_id="456",
        qbo_account_id="456",
        status="pending",
    )
    transaction_sync1.save()
    transaction_sync2.save()


@pytest.mark.asyncio
async def test_get_all_transactions():
    test_value = await get_all_transactions(
        user=Annotated[User, Depends(get_current_user)],
        db=Annotated[Session, Depends(get_db)],
    )

    assert len(test_value) > 1
    assert test_value[0].id == "123"
    assert test_value[1].id == "456"


@pytest.mark.asyncio
async def test_get_transaction_by_id():
    test_value = await get_transaction_by_id(
        user=Annotated[User, Depends(get_current_user)],
        db=Annotated[Session, Depends(get_db)],
        transaction_id="123",
    )

    assert test_value.id == "123"
    assert test_value.created == 123
    assert test_value.type == "charge"
    assert test_value.amount == 1000
    assert test_value.description == "Test Charge"
    assert test_value.stripe_id == "123"
    assert test_value.qbo_account_id == "123"
    assert test_value.status == "pending"
