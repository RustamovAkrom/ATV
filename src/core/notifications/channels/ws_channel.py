from core.notifications.ws.backends.base import WSBackend


class WebSocketChannel:
    def __init__(self, backend: WSBackend):
        self.backend = backend

    async def send(self, payload: dict):
        user_id = payload["user_id"]
        await self.backend.publish(user_id, payload)
