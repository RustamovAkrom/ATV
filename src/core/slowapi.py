import inspect

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from core.config import get_settings

settings = get_settings()


def get_rate_limit_key(request: Request) -> str:
    client_ip = request.client.host if request.client else "unknown"
    trusted_proxies = {
        ip.strip()
        for ip in settings.RATE_LIMIT_TRUSTED_PROXIES.split(",")
        if ip.strip()
    }

    # доверяем XFF только от trusted proxy
    if client_ip in trusted_proxies:
        xff = request.headers.get("X-Forwarded-For")
        if xff:
            return xff.split(",")[0].strip()

    return client_ip


limiter = Limiter(
    key_func=get_rate_limit_key,
    storage_uri=settings.RATE_LIMIT_STORAGE_URL,
    enabled=settings.RATE_LIMIT_ENABLED,
)


async def rate_limit_exceeded_handler(
    request: Request,
    exc: Exception,
) -> Response:
    if not isinstance(exc, RateLimitExceeded):
        raise exc

    rate_exc: RateLimitExceeded = exc
    result = _rate_limit_exceeded_handler(request, rate_exc)

    if inspect.isawaitable(result):
        return await result

    return result
