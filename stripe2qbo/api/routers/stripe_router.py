import os
from datetime import datetime
from typing import Annotated, List, Optional

from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import stripe
from dotenv import load_dotenv

from stripe2qbo.stripe.auth import (
    StripeToken,
    generate_auth_token,
    get_auth_url,
)
from stripe2qbo.stripe.models import Account
from stripe2qbo.stripe.stripe_transactions import get_transactions
from stripe2qbo.sync import TransactionSync

from stripe2qbo.db.database import get_db
from stripe2qbo.db.models import User

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
)


async def get_stripe_token(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> StripeToken:
    user_id = request.session.get("user_id")
    user: User | None = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    stripe_account = user.stripe_user_id

    if stripe_account is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = StripeToken(stripe_user_id=stripe_account)

    return token


@router.get("/oauth2")
async def stripe_oauth_url() -> str:
    return get_auth_url()


@router.get("/oauth2/callback")
async def stripe_oauth_callback(
    code: str, request: Request, db: Annotated[Session, Depends(get_db)]
):
    user_id = request.session.get("user_id")
    user: User | None = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = generate_auth_token(code)
    user.stripe_user_id = token.stripe_user_id
    db.commit()
    return RedirectResponse(url="/")


@router.post("/disconnect")
async def disconnect_stripe(request: Request):
    request.session["stripe_token"] = None


@router.get("/info")
async def get_stripe_info(
    token: Annotated[StripeToken, Depends(get_stripe_token)]
) -> Account:
    stripe_user_id = token.stripe_user_id
    account = stripe.Account.retrieve(stripe_user_id)
    return Account(**account.to_dict())


@router.get("/transactions")
async def get_stripe_transactions(
    stripe_token: Annotated[StripeToken, Depends(get_stripe_token)],
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
            account_id=stripe_token.stripe_user_id,
        )
        transactions.extend(txs)

        if len(txs) < 100:
            break
        starting_after = txs[-1].id

    return [TransactionSync(**transaction.model_dump()) for transaction in transactions]
