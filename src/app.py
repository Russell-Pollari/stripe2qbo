import os
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException

import stripe

from dotenv import load_dotenv

from src.qbo.qbo import CompanyInfo
from src.qbo.qbo_request import qbo_request
from src.qbo.qbo_auth import Token, get_auth_token, get_auth_url, get_token
from src.models.stripe_models import Account

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

app = FastAPI()


@app.get("/")
async def index():
    return {"Hello": "World"}


@app.get("/stripe/info")
async def get_stripe_info() -> Account:
    account = stripe.Account.retrieve("acct_1BKtrnAJuIP5eO0D")
    return Account(**account.to_dict())


@app.get("/qbo/oath2")
async def qbo_uth_url() -> str:
    return get_auth_url()


@app.get("/qbo/token")
async def get_qbo_token(code: str, realm_id: str):
    return get_auth_token(code, realm_id)


@app.get("/qbo/info")
async def get_qbo_info(token: Annotated[Token, Depends(get_token)]) -> CompanyInfo:
    realm_id = token.realm_id
    try:
        response = qbo_request(f"/companyinfo/{realm_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return CompanyInfo(**response.json()["CompanyInfo"])
