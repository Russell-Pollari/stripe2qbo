from typing import Annotated, Dict

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)
from stripe2qbo.api.dependencies import get_current_user_ws
from stripe2qbo.db.models import User
from stripe2qbo.db.schemas import TransactionSync

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
    user: Annotated[User, Depends(get_current_user_ws)],
) -> None:
    await websocket.accept()
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
