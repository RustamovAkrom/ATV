from uuid import UUID

from fastapi import WebSocket

from core.notifications.ws.backends.base import WSBackend


class InMemoryWSBackend(WSBackend):
    def __init__(self):
        self.connections: dict[UUID, set[WebSocket]] = {}

    async def connect(self, user_id: UUID, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: UUID, ws: WebSocket):
        conns = self.connections.get(user_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            self.connections.pop(user_id, None)

    async def publish(self, user_id: UUID, payload: dict):
        for ws in list(self.connections.get(user_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                # соединение умерло — удаляем
                self.disconnect(user_id, ws)
