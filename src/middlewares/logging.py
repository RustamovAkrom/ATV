import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        logger = getattr(request.state, "logger", None)

        if logger:
            logger.info(f"{request.method} {request.url.path} started")

        try:
            response = await call_next(request)
        except Exception:
            if logger:
                logger.exception("Request failed")
            raise

        duration = round((time.perf_counter() - start) * 1000, 2)

        if logger:
            logger.info(
                f"{request.method} {request.url.path} "
                f"{request.status_code} {duration}ms"
            )

        return response
