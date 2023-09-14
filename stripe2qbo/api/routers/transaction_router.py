from typing import Annotated, List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from stripe2qbo.api.dependencies import get_current_user, get_db
from stripe2qbo.db.models import User, TransactionSync as TransactionSyncORM

from stripe2qbo.db.schemas import TransactionSync

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


@router.get("/")
async def get_all_transactions(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[TransactionSync]:
    transactions = (
        db.query(TransactionSyncORM).filter(TransactionSyncORM.user_id == user.id).all()
    )
    if transactions is None:
        raise HTTPException(status_code=404, detail="No transactions found")
    return [
        TransactionSync.model_validate(tsx, from_attributes=True)
        for tsx in transactions
    ]


@router.get("/{transaction_id}")
async def get_transaction_by_id(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    transaction_id: str,
) -> TransactionSync:
    transaction = (
        db.query(TransactionSyncORM)
        .filter(TransactionSyncORM.user_id == user.id)
        .filter(TransactionSyncORM.id == transaction_id)
        .first()
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionSync.model_validate(transaction, from_attributes=True)
