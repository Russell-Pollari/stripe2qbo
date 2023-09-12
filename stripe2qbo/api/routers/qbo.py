from typing import Annotated

from sqlalchemy.orm import Session
from starlette.requests import Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from stripe2qbo.qbo.models import CompanyInfo
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.qbo.auth import (
    Token,
    generate_auth_token,
    get_auth_url,
)
from stripe2qbo.api.dependencies import get_db, get_qbo_token
from stripe2qbo.db.models import User, QBOToken

router = APIRouter(
    prefix="/qbo",
    tags=["qbo"],
)


@router.get("/oauth2")
def qbo_uth_url() -> str:
    return get_auth_url()


@router.get("/oauth2/callback")
def qbo_oauth_callback(
    code: str, realmId: str, request: Request, db: Annotated[Session, Depends(get_db)]
):
    token = generate_auth_token(code, realmId)

    user = db.query(User).filter(User.qbo_realm_id == realmId).first()
    if user is None:
        user = User(qbo_realm_id=realmId)
        db.add(user)
        db.commit()
        db.refresh(user)

    qbo_token = db.query(QBOToken).filter(QBOToken.user_id == user.id).first()
    if qbo_token is None:
        qbo_token = QBOToken(**token.model_dump(), user_id=user.id)
        db.add(qbo_token)
        db.commit()
    else:
        qbo_token.access_token = token.access_token
        qbo_token.refresh_token = token.refresh_token
        qbo_token.expires_at = token.expires_at
        qbo_token.refresh_token_expires_at = token.refresh_token_expires_at
        db.commit()

    request.session["user_id"] = user.id
    # TODO jwt token
    return RedirectResponse("/")


@router.get("/info")
async def get_qbo_info(token: Annotated[Token, Depends(get_qbo_token)]) -> CompanyInfo:
    try:
        response = qbo_request(
            f"/companyinfo/{token.realm_id}",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return CompanyInfo(**response.json()["CompanyInfo"])


@router.get("/accounts")
async def get_qbo_accounts(token: Annotated[Token, Depends(get_qbo_token)]):
    try:
        response = qbo_request(
            "/query?query=select * from Account MAXRESULTS 1000",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"]["Account"]


@router.get("/vendors")
async def get_qbo_vendors(token: Annotated[Token, Depends(get_qbo_token)]):
    try:
        response = qbo_request(
            "/query?query=select * from Vendor MAXRESULTS 1000",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"]["Vendor"]


@router.get("/taxcodes")
async def get_qbo_taxcodes(token: Annotated[Token, Depends(get_qbo_token)]):
    try:
        response = qbo_request(
            "/query?query=select * from TaxCode MAXRESULTS 1000",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"].get("TaxCode", [])
