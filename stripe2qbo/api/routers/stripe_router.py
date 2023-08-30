import os
from typing import Annotated
from starlette.requests import Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import stripe
from dotenv import load_dotenv

from stripe2qbo.stripe.auth import (
    StripeToken,
    delete_token_file,
    generate_auth_token,
    get_auth_url,
)
from stripe2qbo.stripe.models import Account

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
)


async def get_stripe_token(request: Request) -> StripeToken:
    token = request.session.get("stripe_token")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = StripeToken(**token)

    return token


@router.get("/oauth2")
async def stripe_oauth_url() -> str:
    return get_auth_url()


@router.get("/oauth2/callback")
async def stripe_oauth_callback(code: str, request: Request):
    token = generate_auth_token(code)
    request.session["stripe_token"] = token.model_dump()
    return RedirectResponse("/")


@router.post("/disconnect")
async def disconnect_stripe(request: Request):
    request.session["stripe_token"] = None
    delete_token_file()


@router.get("/info")
async def get_stripe_info(
    token: Annotated[StripeToken, Depends(get_stripe_token)]
) -> Account:
    stripe_user_id = token.stripe_user_id
    account = stripe.Account.retrieve(stripe_user_id)
    return Account(**account.to_dict())
