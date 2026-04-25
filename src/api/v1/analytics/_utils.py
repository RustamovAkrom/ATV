import time
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone

from fastapi import HTTPException, Request
from loguru import logger

from core.cache.manager import cache
from core.config import get_settings

settings = get_settings()


def parse_optional_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="Invalid datetime format. Use ISO 8601."
        ) from exc

    # Normalize naive inputs to UTC to keep analytics ranges deterministic.
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def sanitize_search(value: str | None) -> str | None:
    if value is None:
        return None

    cleaned = " ".join(
        value.replace("%", " ").replace("_", " ").replace("*", " ").split()
    )
    if not cleaned:
        return None

    return cleaned[: settings.ANALYTICS_SEARCH_MAX_LENGTH]


async def enforce_rate_limit(
    request: Request, scope: str, limit: int, window_seconds: int = 60
) -> None:
    user_id = getattr(request.state, "user_id", None)
    client_ip = request.client.host if request.client else "unknown"
    identity = str(user_id or client_ip)
    bucket = int(time.time() // window_seconds)
    key = f"rate:{scope}:{identity}:{bucket}"

    current = await cache.backend.incr(key)
    if current == 1:
        await cache.backend.set(key, str(current), window_seconds)

    if current > limit:
        raise HTTPException(status_code=429, detail="Too many requests")


def parse_rate_limit(config_value: str) -> tuple[int, int]:
    try:
        amount_raw, period_raw = config_value.split("/", 1)
        amount = max(int(amount_raw.strip()), 1)
    except (AttributeError, TypeError, ValueError):
        return 20, 60

    period = period_raw.strip().lower()
    if period.startswith("hour"):
        return amount, 3600
    if period.startswith("second"):
        return amount, 1
    return amount, 60


async def run_analytics_operation(
    request: Request,
    endpoint_name: str,
    filters: dict,
    operation: Callable[[], Awaitable],
    fallback_factory: Callable[[], object],
):
    started_at = time.perf_counter()
    safe_filters = {key: value for key, value in filters.items() if value is not None}

    try:
        result = await operation()
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "Analytics operation failed",
            endpoint=endpoint_name,
            filters=safe_filters,
            duration_ms=duration_ms,
            path=request.url.path,
        )
        return fallback_factory()

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    logger.info(
        "Analytics operation completed",
        endpoint=endpoint_name,
        filters=safe_filters,
        duration_ms=duration_ms,
        path=request.url.path,
    )
    return result
