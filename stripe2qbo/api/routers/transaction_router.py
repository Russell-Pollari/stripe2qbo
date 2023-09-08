from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from stripe2qbo.api.dependencies import get_current_user, get_db
from stripe2qbo.db.models import TransactionSync, User

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"],
)


@router.get("/")
async def get_all_transactions(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> TransactionSync:
    try:
        return (
            db.query(TransactionSync).filter(TransactionSync.user_id == user.id).all()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error making request: {e}")


@router.get("/{Transaction_id}")
async def get_transaction_by_id(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    Transaction_id: str,
) -> TransactionSync:
    try:
        return (
            db.query(TransactionSync)
            .filter(
                TransactionSync.user_id == user.id, TransactionSync.id == Transaction_id
            )
            .first()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error making request: {e}")
