from uuid import UUID

from fastapi import WebSocket


class WebSocketManager:
    """
    Connection manager (как у тебя в audit)
    """

    def __init__(self):
        self.connections: dict[UUID, set[WebSocket]] = {}

    async def connect(self, user_id: UUID, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: UUID, ws: WebSocket):
        if user_id in self.connections:
            self.connections[user_id].discard(ws)
            if not self.connections[user_id]:
                del self.connections[user_id]

    async def send_to_user(self, user_id: UUID, data: dict):
        for ws in self.connections.get(user_id, []):
            await ws.send_json(data)


def get_ws_manager():
    return WebSocketManager()
