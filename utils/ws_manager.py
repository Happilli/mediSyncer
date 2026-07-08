import asyncio

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}
        self.loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket):
        connections = self.active_connections.get(user_id)
        if connections and websocket in connections:
            connections.remove(websocket)
        if connections is not None and len(connections) == 0:
            self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, data: dict):
        connections = self.active_connections.get(user_id)
        if not connections:
            return
        dead = []
        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    def schedule_send(self, user_id: int, data: dict):
        if self.loop is None:
            return
        asyncio.run_coroutine_threadsafe(self.send_to_user(user_id, data), self.loop)


manager = ConnectionManager()
