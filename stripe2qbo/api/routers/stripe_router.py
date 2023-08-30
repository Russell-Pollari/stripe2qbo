import os
from datetime import datetime
from typing import Annotated, List, Optional
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
from stripe2qbo.stripe.stripe_transactions import get_transactions
from stripe2qbo.sync import TransactionSync

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
    return RedirectResponse(url="/")


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


@router.get("/transactions", dependencies=[Depends(get_stripe_token)])
async def get_stripe_transactions(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> List[TransactionSync]:
    from_timestamp = (
        int(datetime.strptime(from_date, "%Y-%m-%d").timestamp()) if from_date else None
    )
    to_timestamp = (
        int(datetime.strptime(to_date, "%Y-%m-%d").timestamp()) if to_date else None
    )

    transactions = []
    starting_after: str | None = None
    while True:
        txs = get_transactions(
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            starting_after=starting_after,
        )
        transactions.extend(txs)

        if len(txs) < 100:
            break
        starting_after = txs[-1].id

    return [TransactionSync(**transaction.model_dump()) for transaction in transactions]
