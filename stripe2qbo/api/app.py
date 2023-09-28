from typing import Optional, Annotated, List
import asyncio
import os

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import (
    Depends,
    FastAPI,
    Query,
    Request,
    BackgroundTasks,
    WebSocketException,
)
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.Stripe2QBO import Stripe2QBO
from stripe2qbo.api.routers import qbo, stripe_router, transaction_router
from stripe2qbo.api.dependencies import (
    get_db,
    get_stripe_user_id,
    get_qbo_token,
    get_current_user,
)
from stripe2qbo.api.routers.sync_webhook import manager, router as sync_router
from stripe2qbo.qbo.auth import Token
from stripe2qbo.db.models import SyncSettings, User
from stripe2qbo.db.models import TransactionSync as TransactionSyncORM
from stripe2qbo.db.schemas import Settings

load_dotenv()


app = FastAPI()

if not os.path.exists("static"):
    os.mkdir("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

app.include_router(qbo.router, prefix="/api")
app.include_router(stripe_router.router, prefix="/api")
app.include_router(transaction_router.router, prefix="/api")
app.include_router(sync_router, prefix="/api")


@app.get("/api/userId")
async def user_id(user: Annotated[User, Depends(get_current_user)]) -> int:
    return user.id


@app.post("/api/logout")
async def logout(request: Request) -> None:
    request.session.clear()
    return None


@app.get("/api/settings")
def get_settings(
    token: Annotated[Token, Depends(get_qbo_token)],
    db: Annotated[Session, Depends(get_db)],
) -> Optional[Settings]:
    realm_id = token.realm_id
    query = select(SyncSettings).where(SyncSettings.qbo_realm_id == realm_id)
    sync_settings = db.execute(query).scalar_one_or_none()
    if sync_settings is None:
        return None
    return Settings.model_validate(sync_settings)


@app.post("/api/settings")
def save_settings(
    settings: Settings,
    token: Annotated[Token, Depends(get_qbo_token)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    realm_id = token.realm_id
    query = select(SyncSettings).where(SyncSettings.qbo_realm_id == realm_id)
    sync_settings = db.execute(query).scalar_one_or_none()
    if sync_settings is None:
        sync_settings = SyncSettings(qbo_realm_id=realm_id, **settings.model_dump())
        db.add(sync_settings)
    else:
        update_query = (
            update(SyncSettings)
            .where(SyncSettings.qbo_realm_id == realm_id)
            .values(**settings.model_dump())
        )
        db.execute(update_query)
    db.commit()


def sync_transaction(transaction_id: str, syncer: Stripe2QBO, user: User):
    if user.stripe_user_id is None:
        raise Exception("Stripe user id is not set")
    transaction = get_transaction(transaction_id, account_id=user.stripe_user_id)
    transaction_sync = syncer.sync(transaction, user)
    return transaction_sync


async def sync_transactions(
    transaction_ids: List[str], syncer: Stripe2QBO, user: User, db: Session
):
    for transaction_id in transaction_ids:
        transaction_sync = await asyncio.to_thread(
            sync_transaction, transaction_id, syncer, user
        )
        db.query(TransactionSyncORM).filter(
            TransactionSyncORM.id == transaction_id
        ).update(
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
        try:
            await manager.send_message(user.id, transaction_sync)
        except WebSocketException:
            continue


@app.post("/api/sync")
async def sync(
    transaction_ids: Annotated[List[str], Query()],
    settings: Annotated[Settings, Depends(get_settings)],
    qbo_token: Annotated[Token, Depends(get_qbo_token)],
    user: Annotated[User, Depends(get_current_user)],
    stripe_user_id: Annotated[str, Depends(get_stripe_user_id)],
    db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
) -> str:
    # TODO: Skip already existing transactions
    for transaction_id in transaction_ids:
        db.query(TransactionSyncORM).filter(
            TransactionSyncORM.id == transaction_id
        ).update({"status": "syncing"})
    db.commit()

    syncer = Stripe2QBO(settings, qbo_token)
    user.stripe_user_id = stripe_user_id
    background_tasks.add_task(sync_transactions, transaction_ids, syncer, user, db)

    return "Done"  # TODO: Sync summary


@app.get("/{path:path}")
async def catch_all(path: str) -> HTMLResponse:
    return HTMLResponse(
        content="""
            <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Stripe2QBO</title>
                    <link rel="stylesheet" href="/static/index.css">
                </head>
                <body>
                    <div id="root"></div>
                    <script src="/static/index.js"></script>
                </body>
            </html>
        """,
        status_code=200,
    )
