import asyncio
import os
import hmac
import hashlib

from celery import Celery  # type:ignore
from requests import request

from stripe2qbo.db.database import SessionLocal
from stripe2qbo.db.models import User, TransactionSync
from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.Stripe2QBO import create_stripe2qbo
from stripe2qbo.api.dependencies import get_qbo_token
from stripe2qbo.api.routers.settings import get_settings

BROKER_URL = os.getenv("BROKER_URL", "amqp://localhost")

app = Celery(
    "syncbooks",
    broker=BROKER_URL,
    broker_connection_retry_on_startup=True,
    worker_concurrency=2,
    task_serializer="json",
)


@app.task
def sync_transaction_worker(transaction_id: str, user_id: int):
    asyncio.run(sync_transaction(transaction_id, user_id))


async def sync_transaction(transaction_id: str, user_id: int):
    db = SessionLocal()
    if db is None:
        raise Exception("DB is not set")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise Exception("User is not set")

    qbo_token = get_qbo_token(user, db)
    settings = get_settings(qbo_token, db)

    if settings is None:
        raise Exception("Settings is not set")

    if user.stripe_user_id is None:
        raise Exception("Stripe user id is not set")

    syncer = await create_stripe2qbo(settings, qbo_token)
    transaction = get_transaction(transaction_id, account_id=user.stripe_user_id)
    transaction_sync = await syncer.sync(transaction, user)

    db.query(TransactionSync).filter(TransactionSync.id == transaction_id).update(
        {
            "status": transaction_sync.status,
            "transfer_id": transaction_sync.transfer_id,
            "invoice_id": transaction_sync.invoice_id,
            "payment_id": transaction_sync.payment_id,
            "expense_id": transaction_sync.expense_id,
            "failure_reason": transaction_sync.failure_reason or None,
        }
    )
    db.commit()
    db.close()

    sig = hmac.new(
        os.environ["SECRET_KEY"].encode(),
        transaction_sync.model_dump_json().encode(),
        hashlib.sha256,
    ).hexdigest()

    HOST = os.getenv("HOST", "localhost:8000")
    PROTOCOL = "https" if os.getenv("SSL") else "http"
    try:
        request(
            "POST",
            f"{PROTOCOL}://{HOST}/api/sync/notify?user_id={user_id}",
            headers={"X-Signature": sig},
            data=transaction_sync.model_dump_json(),
        )
    except Exception as e:
        print("Failed to notify", e)

    return "ok"
