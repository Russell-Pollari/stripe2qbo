import asyncio
from typing import Annotated, Dict, List

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    Query,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from stripe2qbo.api.auth import get_current_user_from_token

from stripe2qbo.db.models import User
from stripe2qbo.db.schemas import TransactionSync
from stripe2qbo.qbo.auth import Token
from stripe2qbo.stripe.stripe_transactions import get_transaction
from stripe2qbo.Stripe2QBO import Stripe2QBO
from stripe2qbo.api.dependencies import (
    get_db,
    get_qbo_token,
    get_stripe_user_id,
)
from stripe2qbo.db.models import TransactionSync as TransactionSyncORM
from stripe2qbo.db.schemas import Settings
from stripe2qbo.api.routers.settings import get_settings

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


def sync_transaction(transaction_id: str, syncer: Stripe2QBO, user: User):
    if user.stripe_user_id is None:
        raise Exception("Stripe user id is not set")
    transaction = get_transaction(transaction_id, account_id=user.stripe_user_id)
    transaction_sync = syncer.sync(transaction, user)
    return transaction_sync


async def sync_transactions(
    transaction_ids: List[str], syncer: Stripe2QBO, user: User, db: Session
):
    for transaction_id in transaction_ids:
        transaction_sync = await asyncio.to_thread(
            sync_transaction, transaction_id, syncer, user
        )
        db.query(TransactionSyncORM).filter(
            TransactionSyncORM.id == transaction_id
        ).update(
            {
                "status": transaction_sync.status,
                "transfer_id": transaction_sync.transfer_id,
                "invoice_id": transaction_sync.invoice_id,
                "payment_id": transaction_sync.payment_id,
                "expense_id": transaction_sync.expense_id,
                "failure_reason": transaction_sync.failure_reason or None,
            }
        )
        db.commit()
        try:
            await manager.send_message(user.id, transaction_sync)
        except WebSocketException:
            continue


@router.post("")
async def sync(
    transaction_ids: Annotated[List[str], Query()],
    settings: Annotated[Settings, Depends(get_settings)],
    qbo_token: Annotated[Token, Depends(get_qbo_token)],
    user: Annotated[User, Depends(get_current_user_from_token)],
    stripe_user_id: Annotated[str, Depends(get_stripe_user_id)],
    db: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
) -> str:
    db.query(TransactionSyncORM).filter(
        TransactionSyncORM.id.in_(transaction_ids)
    ).update({"status": "syncing"})
    db.commit()

    syncer = Stripe2QBO(settings, qbo_token)
    user.stripe_user_id = stripe_user_id
    background_tasks.add_task(sync_transactions, transaction_ids, syncer, user, db)

    return "ok"
