import os
from typing import Annotated, Dict, Any, Literal
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
    stripe_user_id = os.getenv("STRIPE_ACCOUNT_ID", user.stripe_user_id)
    if stripe_user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return stripe_user_id


CurrencyLitList = Literal[
    "aed",
    "afn",
    "all",
    "amd",
    "ang",
    "aoa",
    "ars",
    "aud",
    "awg",
    "azn",
    "bam",
    "bbd",
    "bdt",
    "bgn",
    "bif",
    "bmd",
    "bnd",
    "bob",
    "brl",
    "bsd",
    "bwp",
    "byn",
    "bzd",
    "cad",
    "cdf",
    "chf",
    "clp",
    "crc",
    "cve",
    "czk",
    "djf",
    "dkk",
    "dop",
    "dzd",
    "egp",
    "eur",
    "etb",
    "eth",
    "fjd",
    "fkp",
    "gbp",
    "gel",
    "ghs",
    "gip",
    "gmd",
    "gtq",
    "gyd",
    "hkd",
    "hnl",
    "htg",
    "huf",
    "idr",
    "ils",
    "inr",
    "irr",
    "isk",
    "jmd",
    "jod",
    "jpy",
    "kes",
    "kgs",
    "khr",
    "kmf",
    "kgs",
    "khr",
    "kmf",
    "krw",
    "kwd",
    "kzt",
    "lak",
    "lbp",
    "lkr",
    "lrd",
    "lsl",
    "mad",
    "mdl",
    "mga",
    "mkd",
    "mmk",
    "mnt",
    "mop",
    "mur",
    "mvr",
    "mwk",
    "mxn",
    "myr",
    "mzn",
    "nad",
    "ngn",
    "nio",
    "nok",
    "npr",
    "omr",
    "pab",
    "pen",
    "pgk",
    "php",
    "pkr",
    "pln",
    "pyg",
    "qar",
    "ron",
    "rsd",
    "rub",
    "rwf",
    "sar",
    "scr",
    "sek",
    "sgd",
    "shp",
    "sos",
    "srd",
    "std",
    "svc",
    "szl",
    "thb",
    "tjs",
    "tmt",
    "tnd",
    "top",
    "try",
    "ttd",
    "twd",
    "tzs",
    "uah",
    "ugx",
    "usd",
    "uyu",
    "uzs",
    "vef",
    "vuv",
    "wst",
    "xaf",
    "xcd",
    "xof",
    "xpf",
    "yer",
    "zar",
    "zmw",
]

CurrencyList = [
    "aed",
    "afn",
    "all",
    "amd",
    "ang",
    "aoa",
    "ars",
    "aud",
    "awg",
    "azn",
    "bam",
    "bbd",
    "bdt",
    "bgn",
    "bif",
    "bmd",
    "bnd",
    "bob",
    "brl",
    "bsd",
    "bwp",
    "byn",
    "bzd",
    "cad",
    "cdf",
    "chf",
    "clp",
    "crc",
    "cve",
    "czk",
    "djf",
    "dkk",
    "dop",
    "dzd",
    "egp",
    "eur",
    "etb",
    "eth",
    "fjd",
    "fkp",
    "gbp",
    "gel",
    "ghs",
    "gip",
    "gmd",
    "gtq",
    "gyd",
    "hkd",
    "hnl",
    "htg",
    "huf",
    "idr",
    "ils",
    "inr",
    "iqd",
    "irr",
    "isk",
    "jmd",
    "jod",
    "jpy",
    "kes",
    "kgs",
    "khr",
    "kmf",
    "kgs",
    "khr",
    "kmf",
    "krw",
    "kwd",
    "kzt",
    "lak",
    "lbp",
    "lkr",
    "lrd",
    "lsl",
    "mad",
    "mdl",
    "mga",
    "mkd",
    "mmk",
    "mnt",
    "mop",
    "mur",
    "mvr",
    "mwk",
    "mxn",
    "myr",
    "mzn",
    "nad",
    "ngn",
    "nio",
    "nok",
    "npr",
    "omr",
    "pab",
    "pen",
    "pgk",
    "php",
    "pkr",
    "pln",
    "pyg",
    "qar",
    "ron",
    "rsd",
    "rub",
    "rwf",
    "sar",
    "scr",
    "sek",
    "sgd",
    "shp",
    "sos",
    "srd",
    "std",
    "svc",
    "szl",
    "thb",
    "tjs",
    "tmt",
    "tnd",
    "top",
    "try",
    "ttd",
    "twd",
    "tzs",
    "uah",
    "ugx",
    "usd",
    "uyu",
    "uzs",
    "vef",
    "vuv",
    "wst",
    "xaf",
    "xcd",
    "xof",
    "xpf",
    "yer",
    "zar",
    "zmw",
]
