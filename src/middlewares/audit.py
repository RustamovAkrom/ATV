# src/core/audit/middleware.py

import time
import uuid
import asyncio

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from core.config import get_settings
from core.database.db_async import get_async_session_factory
from tasks.audit_task import process_audit_log_task
from repositories.audit_repo import AuditRepository


class AuditMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.settings = get_settings()

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        start = time.perf_counter()

        request_id = scope.get("state", {}).get("request_id") or str(uuid.uuid4())
        scope.setdefault("state", {})["request_id"] = request_id

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
                print("AUDIT task")
                if self.settings.ENV == "prod":
                    process_audit_log_task.delay(payload)

                else:
                    async def run():
                        session_factory = get_async_session_factory()

                        async with session_factory() as session:
                            async with session.begin():
                                repo = AuditRepository(session)
                                await repo.create(payload)

                    try:
                        asyncio.create_task(run())
                    except RuntimeError as e:
                        print("Runtime error: ", e)
                        # если нет loop (например sync контекст)
                        asyncio.run(run())

            await send(message)

        await self.app(scope, receive, send_wrapper)
