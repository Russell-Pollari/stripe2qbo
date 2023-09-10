import os
from typing import Annotated, Dict, Any
from datetime import datetime

from fastapi import Depends, HTTPException, Request, WebSocket
from sqlalchemy.orm import Session

from stripe2qbo.db.database import SessionLocal
from stripe2qbo.db.models import User, QBOToken
from stripe2qbo.qbo.auth import Token, refresh_auth_token


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_current_user(
    session: Dict[str, Any],
    db: Session,
) -> User:
    user_id = session.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user


def get_current_user(request: Request, db: Annotated[Session, Depends(get_db)]) -> User:
    return _get_current_user(request.session, db)


def get_current_user_ws(
    websocket: WebSocket, db: Annotated[Session, Depends(get_db)]
) -> User:
    return _get_current_user(websocket.session, db)


def get_qbo_token(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Token:
    token = db.query(QBOToken).filter(QBOToken.user_id == user.id).first()

    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if datetime.fromisoformat(token.refresh_token_expires_at) < datetime.now():
        raise HTTPException(status_code=401, detail="Access token expired")

    if datetime.fromisoformat(token.expires_at) < datetime.now():
        refreshed_token = refresh_auth_token(token.refresh_token, token.realm_id)

        token.access_token = refreshed_token.access_token
        token.refresh_token = refreshed_token.refresh_token
        token.expires_at = refreshed_token.expires_at
        token.refresh_token_expires_at = refreshed_token.refresh_token_expires_at
        db.commit()
        db.refresh(token)

    return Token.model_validate(token, from_attributes=True)


def get_stripe_user_id(user: Annotated[User, Depends(get_current_user)]) -> str:
    return os.getenv("STRIPE_ACCOUNT_ID", "")
    # stripe_user_id = user.stripe_user_id
    # if stripe_user_id is None:
    #     raise HTTPException(status_code=401, detail="Not authenticated")

    # return stripe_user_id
