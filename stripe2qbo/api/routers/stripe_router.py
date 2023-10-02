import os
from datetime import datetime
from typing import Annotated, Optional

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
import stripe
from dotenv import load_dotenv
from stripe2qbo.api.auth import get_current_user_from_token

from stripe2qbo.stripe.auth import (
    generate_auth_token,
    get_auth_url,
)
from stripe2qbo.stripe.models import Account
from stripe2qbo.stripe.stripe_transactions import get_transactions
from stripe2qbo.db.schemas import TransactionSync
from stripe2qbo.api.dependencies import get_db, get_stripe_user_id
from stripe2qbo.db.models import User
from stripe2qbo.db.models import TransactionSync as TransactionSyncORM

load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

router = APIRouter(
    prefix="/stripe",
    tags=["stripe"],
)


@router.get("/oauth2")
async def stripe_oauth_url() -> str:
    return get_auth_url()


@router.post("/oauth2/callback")
async def stripe_oauth_callback(
    code: str,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user_from_token)],
):
    token = generate_auth_token(code)
    db.query(User).filter(User.id == user.id).update(
        {"stripe_user_id": token.stripe_user_id}
    )
    db.commit()
    return "ok"


@router.post("/disconnect")
async def disconnect_stripe(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user_from_token)],
) -> None:
    if os.getenv("STRIPE_ACCOUNT_ID") is not None:
        raise HTTPException(
            status_code=400, detail="Not allowed while STRIPE_ACCOUNT_ID is set"
        )
    db.query(User).filter(User.id == user.id).update({"stripe_user_id": None})
    db.commit()


@router.get("/info")
async def get_stripe_info(
    stripe_user_id: Annotated[str, Depends(get_stripe_user_id)],
) -> Account:
    account = stripe.Account.retrieve(stripe_user_id)
    return Account(**account.to_dict())


@router.post("/transactions")
async def get_stripe_transactions(
    user: Annotated[User, Depends(get_current_user_from_token)],
    stripe_user_id: Annotated[str, Depends(get_stripe_user_id)],
    db: Annotated[Session, Depends(get_db)],
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
) -> str:
    from_timestamp = (
        int(datetime.strptime(from_date, "%Y-%m-%d").timestamp()) if from_date else None
    )
    to_timestamp = (
        int(datetime.strptime(to_date, "%Y-%m-%d").timestamp()) if to_date else None
    )

    transactions = []
    starting_after: str | None = None
    while True:
        txns = get_transactions(
            stripe_user_id,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            starting_after=starting_after,
        )
        transactions.extend(txns)

        for txn in txns:
            t = TransactionSync(
                stripe_id=stripe_user_id,
                user_id=user.id,
                status="pending",
                **txn.model_dump()
            )
            is_imported = (
                db.query(TransactionSyncORM)
                .where(TransactionSyncORM.id == t.id)
                .first()
                is not None
            )
            if not is_imported:
                db.add(TransactionSyncORM(**t.model_dump()))

        db.commit()
        if len(txns) < 100:
            break
        starting_after = txns[-1].id

    return "Done"  # TODO: import summary
