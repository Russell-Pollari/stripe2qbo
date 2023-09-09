import pytest

from stripe2qbo.api.routers.transaction_router import (
    get_all_transactions,
    get_transaction_by_id,
)

from stripe2qbo.db.models import TransactionSync, User, QBOToken
from stripe2qbo.db.database import SessionLocal

db = SessionLocal()

pytest_plugins = ("pytest_asyncio",)


def create_user():
    test_qbo_token = QBOToken(
        realm_id="88584198",
        access_token="123",
        refresh_token="123",
        expires_at="123",
        refresh_token_expires_at="123",
        user_id=1,
    )
    db.add(test_qbo_token)
    db.commit()
    db.refresh(test_qbo_token)

    test_user = User(
        id=831838932,
        qbo_realm_id="88584198",
        stripe_user_id="1234",
        qbo_token=test_qbo_token,
    )

    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    return test_user


def create_transactionSyncs():
    transaction_sync1 = TransactionSync(
        id="124",
        user_id=831838932,
        created=123,
        type="charge",
        amount=1000,
        description="Test Charge",
        stripe_id="123",
        qbo_account_id="123",
        status="pending",
    )
    db.add(transaction_sync1)
    db.commit()
    db.refresh(transaction_sync1)

    transaction_sync2 = TransactionSync(
        id="452",
        user_id=831838932,
        created=456,
        type="charge",
        amount=1000,
        description="Test Charge",
        stripe_id="123",
        qbo_account_id="123",
        status="pending",
    )

    db.add(transaction_sync2)
    db.commit()
    db.refresh(transaction_sync2)


def remove_transactionSyncs():
    db.query(TransactionSync).delete()
    db.commit()


def remove_user():
    db.query(User).delete()
    db.commit()


def remove_qbo_token():
    db.query(QBOToken).delete()
    db.commit()


test_user = create_user()
create_transactionSyncs()


@pytest.mark.asyncio
async def test_get_all_transactions():
    test_value = await get_all_transactions(test_user, db)

    assert len(test_value) > 1
    assert test_value[0].id == "123"
    assert test_value[1].id == "456"


@pytest.mark.asyncio
async def test_get_transaction_by_id():
    test_value = await get_transaction_by_id(test_user, db, 831838932)

    assert test_value.id == "123"
    assert test_value.created == 123
    assert test_value.type == "charge"
    assert test_value.amount == 1000
    assert test_value.description == "Test Charge"
    assert test_value.stripe_id == "123"
    assert test_value.qbo_account_id == "123"
    assert test_value.status == "pending"


remove_transactionSyncs()
remove_user()
remove_qbo_token()
