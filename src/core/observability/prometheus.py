from __future__ import annotations

import os

from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client import REGISTRY as DEFAULT_REGISTRY
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
    multiprocess,
)
from starlette.responses import Response as StarletteResponse

from core.config import get_settings

settings = get_settings()
APP_NAME = settings.APP_NAME


# REGISTRY (MULTIPROCESS SAFE)
def _build_registry() -> CollectorRegistry:
    if os.getenv("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)  # type: ignore[no-untyped-call]
        return registry

    return DEFAULT_REGISTRY


REGISTRY = _build_registry()

# METRICS
REQUEST_TOTAL = Counter(
    f"{APP_NAME}_requests_total",
    "Total HTTP requests",
    ["app", "method", "endpoint", "status"],
    registry=REGISTRY,
)

# NEW: status class counter (2xx / 4xx / 5xx)
REQUEST_STATUS_CLASS = Counter(
    f"{APP_NAME}_requests_by_status_class_total",
    "Total HTTP requests grouped by status class",
    ["app", "method", "endpoint", "status_class"],
    registry=REGISTRY,
)

REQUEST_DURATION = Histogram(
    f"{APP_NAME}_request_duration_seconds",
    "HTTP request duration",
    ["app", "method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
    registry=REGISTRY,
)

REQUEST_ERRORS = Counter(
    f"{APP_NAME}_request_errors_total",
    "Total HTTP error responses",
    ["app", "method", "endpoint", "status"],
    registry=REGISTRY,
)

EXCEPTIONS_TOTAL = Counter(
    f"{APP_NAME}_exceptions_total",
    "Total unhandled exceptions",
    ["app", "endpoint"],
    registry=REGISTRY,
)

IN_PROGRESS = Gauge(
    f"{APP_NAME}_requests_in_progress",
    "Requests currently in progress",
    ["app"],
    registry=REGISTRY,
)

APP_INFO = Info(
    f"{APP_NAME}_app",
    "Application information",
    registry=REGISTRY,
)

APP_INFO.info(
    {
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
    }
)


# METRICS ENDPOINT
async def metrics_endpoint() -> StarletteResponse:
    data = generate_latest(REGISTRY)
    return StarletteResponse(data, media_type=CONTENT_TYPE_LATEST)
