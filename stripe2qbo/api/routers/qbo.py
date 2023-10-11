from typing import Annotated

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from stripe2qbo.qbo.models import CompanyInfo
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.qbo.auth import (
    Token,
    generate_auth_token,
    get_auth_url,
)
from stripe2qbo.api.dependencies import get_db, get_qbo_token
from stripe2qbo.db.models import User, QBOToken
from stripe2qbo.api.auth import get_current_user_from_token

router = APIRouter(
    prefix="/qbo",
    tags=["qbo"],
)


@router.get("/oauth2")
def qbo_uth_url() -> str:
    return get_auth_url()


@router.post("/oauth2/callback")
def qbo_oauth_callback(
    code: str,
    realmId: str,
    user: Annotated[User, Depends(get_current_user_from_token)],
    db: Annotated[Session, Depends(get_db)],
):
    token = generate_auth_token(code, realmId)

    user_for_realm_id = (
        db.query(User).filter(User.qbo_realm_id == token.realm_id).first()
    )
    if user_for_realm_id is not None and user_for_realm_id.id != user.id:
        raise HTTPException(
            status_code=400,
            detail="This QBO account is already linked to another user",
        )

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

    return "ok"


@router.post("/disconnect")
def disconnect_qbo(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user_from_token)],
) -> None:
    db.query(QBOToken).filter(QBOToken.user_id == user.id).delete()
    db.commit()


@router.get("/info")
async def get_qbo_info(token: Annotated[Token, Depends(get_qbo_token)]) -> CompanyInfo:
    try:
        response = await qbo_request(
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
        response = await qbo_request(
            "/query?query=select * from Account MAXRESULTS 1000",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"].get("Account", [])


@router.get("/vendors")
async def get_qbo_vendors(token: Annotated[Token, Depends(get_qbo_token)]):
    try:
        response = await qbo_request(
            "/query?query=select * from Vendor MAXRESULTS 1000",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"].get("Vendor", [])


@router.get("/taxcodes")
async def get_qbo_taxcodes(token: Annotated[Token, Depends(get_qbo_token)]):
    try:
        response = await qbo_request(
            "/query?query=select * from TaxCode MAXRESULTS 1000",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"].get("TaxCode", [])
