import time
from datetime import UTC, datetime
from typing import Awaitable, Callable

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
        raise HTTPException(status_code=422, detail="Invalid ISO 8601 datetime format") from exc
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def sanitize_search(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.replace("%", " ").replace("_", " ").replace("*", " ").split())
    return cleaned[:settings.ANALYTICS_SEARCH_MAX_LENGTH] if cleaned else None


async def run_analytics_operation(
    request: Request,
    endpoint_name: str,
    params: dict,
    operation: Callable[[], Awaitable],
    fallback_factory: Callable[[], object],
):
    started_at = time.perf_counter()
    try:
        result = await operation()
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info("Analytics completed", endpoint=endpoint_name, params=params, duration_ms=duration_ms)
        return result
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception("Analytics failed", endpoint=endpoint_name, params=params, duration_ms=duration_ms)
        return fallback_factory()
