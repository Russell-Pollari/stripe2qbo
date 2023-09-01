from typing import Optional, Annotated
import os

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, WebSocket, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from stripe2qbo.stripe.auth import StripeToken

from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.sync import TransactionSync, sync_transaction
from stripe2qbo.api.routers import qbo, stripe_router
from stripe2qbo.qbo.auth import Token

from stripe2qbo.db.database import get_db, engine
from stripe2qbo.db.models import Base, SyncSettings
from stripe2qbo.db.schemas import Settings

Base.metadata.create_all(bind=engine)


load_dotenv()


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.include_router(qbo.router)
app.include_router(stripe_router.router)


@app.get("/")
async def index() -> HTMLResponse:
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


@app.get("/settings")
def get_settings(
    token: Annotated[Token, Depends(qbo.get_qbo_token)],
    db: Annotated[Session, Depends(get_db)],
) -> Optional[Settings]:
    realm_id = token.realm_id
    query = select(SyncSettings).where(SyncSettings.qbo_realm_id == realm_id)
    sync_settings = db.execute(query).scalar_one_or_none()
    return Settings.model_validate(sync_settings)


@app.post("/settings")
def save_settings(
    settings: Settings,
    token: Annotated[Token, Depends(qbo.get_qbo_token)],
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
        print(update_query)
        db.execute(update_query)
    db.commit()


@app.post(
    "/sync",
    dependencies=[Depends(qbo.get_qbo_token), Depends(stripe_router.get_stripe_token)],
)
async def sync_single_transaction(
    transaction_id: str,
    settings: Annotated[Settings, Depends(get_settings)],
    qbo_token: Annotated[Token, Depends(qbo.get_qbo_token)],
    stripe_token: Annotated[StripeToken, Depends(stripe_router.get_stripe_token)],
) -> TransactionSync:
    transaction = get_transaction(
        transaction_id, account_id=stripe_token.stripe_user_id
    )
    transaction_sync = sync_transaction(transaction, settings, qbo_token)

    return transaction_sync


@app.websocket(
    "/syncmany",
    dependencies=[Depends(qbo.get_qbo_token), Depends(stripe_router.get_stripe_token)],
)
async def sync_many(
    websocket: WebSocket,
    transaction_ids: Annotated[list[str], Query()],
    settings: Annotated[Settings, Depends(get_settings)],
    qbo_token: Annotated[Token, Depends(qbo.get_qbo_token)],
    stripe_token: Annotated[StripeToken, Depends(stripe_router.get_stripe_token)],
):
    await websocket.accept()
    await websocket.send_json(
        {"status": f"Syncing {len(transaction_ids)} transactions"}
    )
    for transaction_id in transaction_ids:
        transaction = get_transaction(
            transaction_id, account_id=stripe_token.stripe_user_id
        )
        transaction_sync = sync_transaction(transaction, settings, qbo_token)

        await websocket.send_json(
            {
                "transaction": transaction_sync.model_dump(),
            }
        )

    await websocket.close()
