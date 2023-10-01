from typing import Optional, Annotated

from fastapi import Depends, APIRouter
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from stripe2qbo.api.dependencies import get_db, get_qbo_token

from stripe2qbo.db.models import SyncSettings
from stripe2qbo.db.schemas import Settings
from stripe2qbo.qbo.auth import Token

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)


@router.get("/")
def get_settings(
    token: Annotated[Token, Depends(get_qbo_token)],
    db: Annotated[Session, Depends(get_db)],
) -> Optional[Settings]:
    realm_id = token.realm_id
    query = select(SyncSettings).where(SyncSettings.qbo_realm_id == realm_id)
    sync_settings = db.execute(query).scalar_one_or_none()
    if sync_settings is None:
        return None
    return Settings.model_validate(sync_settings)


@router.post("/")
def save_settings(
    settings: Settings,
    token: Annotated[Token, Depends(get_qbo_token)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    realm_id = token.realm_id
    query = select(SyncSettings).where(SyncSettings.qbo_realm_id == realm_id)
    sync_settings = db.execute(query).scalar_one_or_none()
    if sync_settings is None:
        sync_settings = SyncSettings(qbo_realm_id=realm_id, **settings.model_dump())
        db.add(sync_settings)
    else:
        update_query = (
            update(SyncSettings)
            .where(SyncSettings.qbo_realm_id == realm_id)
            .values(**settings.model_dump())
        )
        db.execute(update_query)
    db.commit()
