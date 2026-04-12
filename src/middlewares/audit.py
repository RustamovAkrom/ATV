# src/core/audit/middleware.py

import time
import uuid
import asyncio

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from services.audit_service import save_audit_log


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        start = time.perf_counter()
        request_id = str(uuid.uuid4())

        request.state.request_id = request_id

        response = await call_next(request)

        latency = int((time.perf_counter() - start) * 1000)

        forwarded_for = request.headers.get("x-forwarded-for")
        ip = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else None)
        )

        payload = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "user_id": getattr(request.state, "user_id", None),
            "request_id": request_id,
            "latency_ms": latency,
            "ip": ip,
            "is_suspicious": response.status_code >= 500,
        }

        asyncio.create_task(save_audit_log(payload))

        return response
