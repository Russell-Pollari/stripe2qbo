from celery import Celery

from stripe2qbo.db.database import SessionLocal
from stripe2qbo.db.models import User, TransactionSync
from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.Stripe2QBO import Stripe2QBO
from stripe2qbo.api.dependencies import get_qbo_token
from stripe2qbo.api.routers.settings import get_settings

app = Celery(
    "stripe2qbo",
    broker="amqp://localhost",
    backend="db+sqlite:///stripe2qbo.db",
)


@app.task
def sync_transaction_worker(transaction_id: str, user_id: str):
    db = SessionLocal()
    print("Syncing transaction", transaction_id)
    if db is None:
        raise Exception("DB is not set")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise Exception("User is not set")

    qbo_token = get_qbo_token(user, db)
    settings = get_settings(qbo_token, db)

    if user.stripe_user_id is None:
        raise Exception("Stripe user id is not set")

    syncer = Stripe2QBO(settings, qbo_token)
    transaction = get_transaction(transaction_id, account_id=user.stripe_user_id)
    transaction_sync = syncer.sync(transaction, user)

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

    return transaction_sync
