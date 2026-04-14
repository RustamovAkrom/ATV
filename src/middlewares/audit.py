# src/core/audit/middleware.py

import asyncio
import time
import uuid

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request

from services.audit_service import save_audit_log


class AuditMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        scope["state"]["request_id"] = request_id
        async def send_wrapper(message):
            if message["type"] == "http.response.start":

                latency = int((time.perf_counter() - start) * 1000)

                headers = dict(scope["headers"])
                user_agent = headers.get(b"user-agent", b"").decode()

                forwarded_for = headers.get(b"x-forwarded-for")
                ip = (
                    forwarded_for.decode().split(",")[0].strip()
                    if forwarded_for
                    else scope.get("client")[0] if scope.get("client") else None
                )

                payload = {
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": message["status"],
                    "user_id": scope["state"].get("user_id"),
                    "request_id": request_id,
                    "latency_ms": latency,
                    "ip": ip,
                    "user_agent": user_agent,
                    "query": str(request.query_params),
                    "is_suspicious": message["status"] >= 500,
                }

                asyncio.create_task(save_audit_log(payload))

            await send(message)

        await self.app(scope, receive, send_wrapper)
