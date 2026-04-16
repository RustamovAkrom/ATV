from __future__ import annotations

import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.observability.prometheus import (
    APP_NAME,
    EXCEPTIONS_TOTAL,
    IN_PROGRESS,
    REQUEST_DURATION,
    REQUEST_STATUS_CLASS,
    REQUEST_TOTAL,
    REQUEST_ERRORS,
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if request.url.path.startswith("/metrics"):
            return await call_next(request)

        app_label = APP_NAME
        method = request.method

        route = request.scope.get("route")
        endpoint = route.path if route else request.url.path

        start_time = time.perf_counter()
        IN_PROGRESS.labels(app=app_label).inc()

        try:
            response = await call_next(request)
            status_code = response.status_code
            status = str(status_code)

        except Exception:
            EXCEPTIONS_TOTAL.labels(
                app=app_label,
                endpoint=endpoint,
            ).inc()

            REQUEST_ERRORS.labels(
                app=app_label,
                method=method,
                endpoint=endpoint,
                status="500",
            ).inc()

            IN_PROGRESS.labels(app=app_label).dec()
            raise

        duration = time.perf_counter() - start_time

        # total
        REQUEST_TOTAL.labels(
            app=app_label,
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()

        # histogram
        REQUEST_DURATION.labels(
            app=app_label,
            method=method,
            endpoint=endpoint,
        ).observe(duration)

        # status class (2xx / 4xx / 5xx)
        status_class = f"{status_code // 100}xx"
        REQUEST_STATUS_CLASS.labels(
            app=app_label,
            method=method,
            endpoint=endpoint,
            status_class=status_class,
        ).inc()

        # errors
        if status_code >= 400:
            REQUEST_ERRORS.labels(
                app=app_label,
                method=method,
                endpoint=endpoint,
                status=status,
            ).inc()

        IN_PROGRESS.labels(app=app_label).dec()

        return response
