from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from core.logger import bind_logger
from core.config import get_settings


settings = get_settings()


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # 🔥 единый источник
        request.state.request_id = request_id
        request.scope["state"]["request_id"] = request_id

        if settings.LOG_INCLUDE_REQUEST_ID:
            request.state.logger = bind_logger(request_id)

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response
