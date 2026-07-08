import os

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlmodel import select

from database import get_session
from models.users import Users
from utils.ws_manager import manager

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/notifications")
async def notifications_ws(websocket: WebSocket, token: str = Query(...)):
    session_gen = get_session()
    session = next(session_gen)
    try:
        try:
            payload = jwt.decode(
                token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
            )
            user_id = int(payload.get("sub"))
        except (JWTError, TypeError, ValueError):
            await websocket.close(code=4001)
            return

        user = session.exec(select(Users).where(Users.id == user_id)).first()
        if user is None or not user.is_active:
            await websocket.close(code=4001)
            return

        await manager.connect(user_id, websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(user_id, websocket)
    finally:
        session.close()
