import asyncio
import time
import uuid

from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from core.audit.stream import audit_stream
from core.config import get_settings
from core.database.db_async import get_async_session_factory
from repositories.audit_repo import AuditRepository
from schemas.audit import AuditCreateSchema, AuditStreamSchema
from services.audit_service import AuditService
from tasks.audit_task import process_audit_log_task


def _get_level(status: int) -> str:
    if status >= 500:
        return "critical"
    if status >= 400:
        return "warning"
    return "info"


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

        state = scope.setdefault("state", {})
        request_id = getattr(request.state, "request_id", None) or state.get(
            "request_id"
        )
        if not request_id:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        state["request_id"] = request_id

        logger = getattr(request.state, "logger", None)

        async def safe_publish(event: dict):
            try:
                await audit_stream.publish(event)
            except Exception as exc:
                if logger:
                    logger.warning("audit_stream_publish_failed", error=str(exc))

        async def persist_dev(payload: AuditCreateSchema):
            try:
                session_factory = get_async_session_factory()
                async with session_factory() as session:
                    async with session.begin():
                        service = AuditService(AuditRepository(session))
                        await service.persist_audit(payload)
            except Exception as exc:
                if logger:
                    logger.warning("audit_persist_failed", error=str(exc))

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

                status_code = message["status"]

                base_payload = {
                    "method": scope["method"],
                    "path": scope["path"],
                    "status_code": status_code,
                    "user_id": state.get("user_id"),
                    "request_id": request_id,
                    "latency_ms": latency,
                    "ip": ip,
                    "user_agent": user_agent,
                    "query": str(request.query_params) or None,
                    "is_suspicious": status_code >= 500,
                }

                db_payload = AuditCreateSchema(**base_payload)
                stream_payload = AuditStreamSchema(
                    **base_payload,
                    level=_get_level(status_code),
                    timestamp=time.time(),
                )

                asyncio.create_task(safe_publish(jsonable_encoder(stream_payload)))

                if self.settings.ENV == "prod":
                    process_audit_log_task.delay(jsonable_encoder(db_payload))
                else:
                    asyncio.create_task(persist_dev(db_payload))

            await send(message)

        await self.app(scope, receive, send_wrapper)
