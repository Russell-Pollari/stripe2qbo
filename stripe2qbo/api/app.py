import datetime
from typing import Optional
import os

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import stripe

from dotenv import load_dotenv

from stripe2qbo.settings import Settings, load_from_file, save
from stripe2qbo.stripe.models import Account
from stripe2qbo.stripe.stripe_transactions import get_transactions
from stripe2qbo.sync import sync_transaction
from stripe2qbo.api.routers import qbo

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))
app.include_router(qbo.router)


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


@app.get("/stripe/info")
async def get_stripe_info() -> Account:
    account = stripe.Account.retrieve(os.getenv("STRIPE_ACCOUNT_ID"))
    return Account(**account.to_dict())


@app.get("/settings")
async def get_settings() -> Optional[Settings]:
    return load_from_file()


@app.post("/settings")
async def save_settings(settings: Settings) -> None:
    save(settings)


@app.websocket("/sync")
async def sync(
    websocket: WebSocket,
    from_date: Optional[str] = None,
):
    await websocket.accept()

    from_timestamp = (
        int(datetime.datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        if from_date
        else None
    )
    await websocket.send_text("Fetching transactions from Stripe")
    transactions = get_transactions(
        from_timestamp=from_timestamp,
    )
    await websocket.send_text(f"Syncing {len(transactions)} transactions")
    for transaction in transactions:
        message = sync_transaction(transaction)
        await websocket.send_text(message)

    await websocket.send_text("Done")
    await websocket.close()
