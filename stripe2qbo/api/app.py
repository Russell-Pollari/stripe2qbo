from typing import Optional, Annotated
import os

from fastapi import Depends, FastAPI, WebSocket, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from stripe2qbo.settings import Settings, load_from_file, save
from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.sync import TransactionSync, sync_transaction
from stripe2qbo.api.routers import qbo, stripe_router
from stripe2qbo.qbo.auth import Token

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
async def get_settings(
    token: Annotated[Token, Depends(qbo.get_qbo_token)]
) -> Optional[Settings]:
    realm_id = token.realm_id
    return load_from_file(realm_id)


@app.post("/settings")
async def save_settings(
    settings: Settings, token: Annotated[Token, Depends(qbo.get_qbo_token)]
) -> None:
    realm_id = token.realm_id
    save(realm_id, settings)


@app.post(
    "/sync",
    dependencies=[Depends(qbo.get_qbo_token), Depends(stripe_router.get_stripe_token)],
)
async def sync_single_transaction(transaction_id: str) -> TransactionSync:
    transaction = get_transaction(transaction_id)
    transaction_sync = sync_transaction(transaction)

    return transaction_sync


@app.websocket("/syncmany")
async def sync_many(
    websocket: WebSocket,
    transaction_ids: Annotated[list[str], Query()],
):
    await websocket.accept()
    await websocket.send_json(
        {"status": f"Syncing {len(transaction_ids)} transactions"}
    )
    for transaction_id in transaction_ids:
        transaction = get_transaction(transaction_id)
        transaction_sync = sync_transaction(transaction)

        await websocket.send_json(
            {
                "transaction": transaction_sync.model_dump(),
            }
        )

    await websocket.close()
