import os
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
import stripe

from dotenv import load_dotenv

from src.qbo.qbo import CompanyInfo
from src.qbo.qbo_request import qbo_request
from src.qbo.qbo_auth import Token, get_auth_token, get_auth_url
from src.models.stripe_models import Account

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))


async def get_qbo_token(request: Request) -> Token:
    token = request.session.get("token")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return Token(**token)


@app.get("/")
async def index() -> HTMLResponse:
    return HTMLResponse(
        content="""
            <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <title>Stripe2QBO</title>
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
    account = stripe.Account.retrieve("acct_1BKtrnAJuIP5eO0D")
    return Account(**account.to_dict())


@app.get("/qbo/oauth2")
async def qbo_uth_url() -> str:
    return get_auth_url()


@app.get("/qbocallback")
async def qbo_oauth_callback(code: str, realmId: str, request: Request):
    token = get_auth_token(code, realmId)
    request.session["token"] = token.model_dump()
    return RedirectResponse("/")


@app.get("/qbo/disconnect")
async def disconnect_qbo(request: Request):
    request.session["token"] = None


@app.get("/qbo/info")
async def get_qbo_info(token: Annotated[Token, Depends(get_qbo_token)]) -> CompanyInfo:
    try:
        response = qbo_request(
            f"/companyinfo/{token.realm_id}",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return CompanyInfo(**response.json()["CompanyInfo"])
