from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from stripe2qbo.api.dependencies import get_current_user, get_db
from stripe2qbo.db.models import User

from stripe2qbo.db.schemas import TransactionSync

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


@router.get("/")
async def get_all_transactions(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> TransactionSync:
    return db.query(TransactionSync).filter(TransactionSync.user_id == user.id).all()


@router.get("/{transaction_id}")
async def get_transaction_by_id(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    transaction_id: str,
) -> TransactionSync:
    return (
        db.query(TransactionSync)
        .filter(TransactionSync.user_id == user.id)
        .filter(TransactionSync.id == transaction_id)
        .first()
    )
