from typing import Annotated
from datetime import datetime

from starlette.requests import Request
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse

from stripe2qbo.qbo.models import CompanyInfo
from stripe2qbo.qbo.qbo_request import qbo_request
from stripe2qbo.qbo.auth import (
    Token,
    delete_token_file,
    generate_auth_token,
    get_auth_url,
    refresh_auth_token,
)

router = APIRouter(
    prefix="/qbo",
    tags=["qbo"],
)


async def get_qbo_token(request: Request) -> Token:
    token = request.session.get("token")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = Token(**token)

    if datetime.fromisoformat(token.refresh_token_expires_at) < datetime.now():
        raise HTTPException(status_code=401, detail="Access token expired")

    if datetime.fromisoformat(token.expires_at) < datetime.now():
        token = refresh_auth_token(token.refresh_token, token.realm_id)
        request.session["token"] = token.model_dump()

    return token


@router.get("/oauth2")
async def qbo_uth_url() -> str:
    return get_auth_url()


@router.get("/oauth2/callback")
async def qbo_oauth_callback(code: str, realmId: str, request: Request):
    token = generate_auth_token(code, realmId)
    request.session["token"] = token.model_dump()
    return RedirectResponse("/")


@router.get("/disconnect")
async def disconnect_qbo(request: Request):
    request.session["token"] = None
    delete_token_file()
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
            "/query?query=select * from Account",
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
            "/query?query=select * from Vendor",
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
            "/query?query=select * from TaxCode",
            access_token=token.access_token,
            realm_id=token.realm_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making request: {e}")

    return response.json()["QueryResponse"]["TaxCode"]
