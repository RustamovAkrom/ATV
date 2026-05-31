import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from core.config import get_settings
from core.logger import bind_logger

settings = get_settings()


class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        request_id = headers.get(b"x-request-id", b"").decode() or str(uuid.uuid4())

        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        if settings.LOG_INCLUDE_REQUEST_ID:
            scope["state"]["logger"] = bind_logger(request_id)

        async def send_wrapper(message: Message):
            if message["type"] == "http.response.start":
                response_headers = list(message.get("headers", []))
                response_headers.append((b"X-Request-ID", request_id.encode()))
                message["headers"] = response_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
