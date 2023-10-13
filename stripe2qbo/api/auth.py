import os
from typing import Annotated, Any, Dict, Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Cookie
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from passlib.context import CryptContext

from stripe2qbo.db.database import SessionLocal
from stripe2qbo.db.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"


class AuthToken(BaseModel):
    access_token: str
    token_type: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(email: str, password: str, db: Session) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(email: str) -> tuple[str, datetime]:
    to_encode: Dict[str, Any] = {"sub": email}
    expires = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update(expires=expires.timestamp())
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expires


def get_current_user_from_token(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Cookie()] = None,
) -> User:
    if token is None:
        raise HTTPException(status_code=401, detail="Missing token")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    expires = payload.get("expires")
    if expires is not None:
        expires_at = datetime.fromtimestamp(expires)
        if datetime.utcnow() > expires_at:
            raise HTTPException(status_code=401, detail="Token expired")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid user")

    return user
