from typing import Annotated

from fastapi import APIRouter, Depends

from stripe2qbo.api.dependencies import get_current_user
from stripe2qbo.db.models import TransactionSync, User

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


@router.get("/")
async def get_all_transactions(
    user: Annotated[User, Depends(get_current_user)],
) -> TransactionSync:
    return TransactionSync.query.filter(TransactionSync.user_id == user.id).all()


@router.get("/{transaction_id}")
async def get_transaction_by_id(
    user: Annotated[User, Depends(get_current_user)],
    transaction_id: str,
) -> TransactionSync:
    return (
        TransactionSync.query.filter(TransactionSync.user_id == user.id)
        .filter(TransactionSync.id == transaction_id)
        .first()
    )
