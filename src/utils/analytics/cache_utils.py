import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from loguru import logger


async def run_analytics_operation[T](
    request: Request,
    endpoint_name: str,
    params: dict,
    operation: Callable[[], Awaitable[T]],
    fallback_factory: Callable[[], T],
) -> T:
    """Run an analytics operation with structured logging and fallback output."""
    started_at = time.perf_counter()
    try:
        result = await operation()
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "Analytics completed",
            endpoint=endpoint_name,
            path=str(request.url.path),
            params=params,
            duration_ms=duration_ms,
        )
        return result
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "Analytics failed",
            endpoint=endpoint_name,
            path=str(request.url.path),
            params=params,
            duration_ms=duration_ms,
        )
        return fallback_factory()
