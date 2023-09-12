from typing import Optional, Annotated
import os

from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, WebSocket, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.sync import TransactionSync
from stripe2qbo.Stripe2QBO import Stripe2QBO
from stripe2qbo.api.routers import qbo, stripe_router
from stripe2qbo.api.dependencies import (
    get_current_user_ws,
    get_db,
    get_stripe_user_id,
    get_qbo_token,
    get_current_user,
)
from stripe2qbo.qbo.auth import Token

from stripe2qbo.db.database import engine
from stripe2qbo.db.models import Base, SyncSettings, User
from stripe2qbo.db.schemas import Settings

Base.metadata.create_all(bind=engine)


load_dotenv()


app = FastAPI()

if not os.path.exists("static"):
    os.mkdir("static")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.include_router(qbo.router, prefix="/api")
app.include_router(stripe_router.router, prefix="/api")


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


@app.post("/api/sync")
async def sync_single_transaction(
    transaction_id: str,
    settings: Annotated[Settings, Depends(get_settings)],
    qbo_token: Annotated[Token, Depends(get_qbo_token)],
    stripe_user_id: Annotated[str, Depends(get_stripe_user_id)],
) -> TransactionSync:
    transaction = get_transaction(transaction_id, account_id=stripe_user_id)
    syncer = Stripe2QBO(settings, qbo_token)
    transaction_sync = syncer.sync(transaction)

    return transaction_sync


@app.websocket("/api/syncmany")
async def sync_many(
    websocket: WebSocket,
    transaction_ids: Annotated[list[str], Query()],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user_ws)],
):
    stripe_user_id = os.getenv("STRIPE_ACCOUNT_ID", user.stripe_user_id)

    if stripe_user_id is None:
        await websocket.send_json({"status": "Not authenticated"})
        await websocket.close()
        return

    # Most dependencies are not defined for websocket scope
    settings_orm = (
        db.query(SyncSettings)
        .where(SyncSettings.qbo_realm_id == user.qbo_realm_id)
        .first()
    )
    settings = Settings.model_validate(settings_orm)
    qbo_token = get_qbo_token(user, db)

    syncer = Stripe2QBO(settings, qbo_token)

    await websocket.accept()
    await websocket.send_json(
        {"status": f"Syncing {len(transaction_ids)} transactions"}
    )
    for transaction_id in transaction_ids:
        transaction = get_transaction(
            transaction_id, account_id=os.getenv("STRIPE_ACCOUNT_ID", "")
        )
        transaction_sync = syncer.sync(transaction)

        await websocket.send_json(
            {
                "transaction": transaction_sync.model_dump(),
            }
        )

    await websocket.close()


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
