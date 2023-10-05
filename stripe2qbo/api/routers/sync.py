from typing import Annotated, Dict, List
import hashlib
import hmac
import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Header,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    Query,
)
from sqlalchemy.orm import Session
from stripe2qbo.api.auth import get_current_user_from_token

from stripe2qbo.workers.sync_worker import sync_transaction_worker
from stripe2qbo.db.models import User
from stripe2qbo.db.schemas import TransactionSync
from stripe2qbo.api.dependencies import get_db
from stripe2qbo.db.models import TransactionSync as TransactionSyncORM

router = APIRouter(
    tags=["sync"],
    prefix="/sync",
)


class WebSocketManager:
    def __init__(self) -> None:
        self._clients: Dict[int, WebSocket] = {}

    def register(self, user_id: int, websocket: WebSocket):
        self._clients[user_id] = websocket

    def unregister(self, user_id: int):
        connections = self._clients
        del connections[user_id]
        self._clients = connections

    async def send_message(self, user_id: int, transaction: TransactionSync):
        connection = self._clients.get(user_id)
        if connection is None:
            return
        try:
            await connection.send_json(transaction.model_dump())
        except WebSocketException:
            self.unregister(user_id)


manager = WebSocketManager()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    await websocket.accept()

    # We can't use Headers with websockets, so cannot use oauth2_scheme
    # the client sends the auth token with the first message
    token = await websocket.receive_text()
    user = get_current_user_from_token(token, db)
    manager.register(user.id, websocket)

    while True:
        try:
            await websocket.receive_text()
        except WebSocketException:
            manager.unregister(user.id)
            break
        except WebSocketDisconnect:
            manager.unregister(user.id)
            break


@router.post("/notify")
async def notify(
    user_id: int,
    transaction: TransactionSync,
    X_Signature: Annotated[str | None, Header()] = None,
):
    """Notify the client of a transaction sync status change.
    This is called by the worker and should not callable by an end user"""
    if X_Signature is None:
        raise HTTPException(status_code=401, detail="Missing signature")

    sig = hmac.new(
        os.environ["SECRET_KEY"].encode(),
        transaction.model_dump_json().encode(),
        hashlib.sha256,
    ).hexdigest()

    if sig != X_Signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    await manager.send_message(user_id, transaction)


@router.post("")
def sync(
    transaction_ids: Annotated[List[str], Query()],
    user: Annotated[User, Depends(get_current_user_from_token)],
    db: Annotated[Session, Depends(get_db)],
) -> str:
    try:
        sync_transaction_worker.starmap(
            map(lambda x: (x, user.id), transaction_ids)
        ).delay()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    db.query(TransactionSyncORM).filter(
        TransactionSyncORM.id.in_(transaction_ids)
    ).update({"status": "syncing"})
    db.commit()

    return "ok"
