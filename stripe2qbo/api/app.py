import datetime
from typing import Optional, Annotated
import os

from fastapi import Depends, FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv

from stripe2qbo.settings import Settings, load_from_file, save
from stripe2qbo.stripe.stripe_transactions import get_transactions
from stripe2qbo.sync import sync_transaction
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


@app.websocket("/sync")
async def sync(
    websocket: WebSocket,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
):
    await websocket.accept()

    from_timestamp = (
        int(datetime.datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        if from_date
        else None
    )
    to_timestamp = (
        int(datetime.datetime.strptime(to_date, "%Y-%m-%d").timestamp())
        if to_date
        else None
    )

    starting_after = None  # for pagination
    while True:
        await websocket.send_json({"status": "Fetching Stripe transactions"})
        transactions = get_transactions(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            starting_after=starting_after,
        )
        await websocket.send_json(
            {"status": f"Syncing {len(transactions)} transactions"}
        )
        for transaction in transactions:
            transaction_sync = sync_transaction(transaction)
            await websocket.send_json(
                {
                    "transaction": transaction_sync.model_dump(),
                }
            )

        if len(transactions) < 100:
            break
        starting_after = transactions[-1].id

    await websocket.close()
