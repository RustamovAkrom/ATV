import time
from importlib.metadata import version
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel

from core.observability.prometheus import REGISTRY  # IMPORTANT: use same registry!
from core.config import get_settings

router = APIRouter(tags=["Monitoring"])


# RESPONSE MODELS
class HealthcheckResponse(BaseModel):
    timestamp: int


class StatusResponse(BaseModel):
    app: str = "ok"


class VersionResponse(BaseModel):
    version: str


# BASIC MONITORING
@router.get("/healthcheck", summary="Service healthcheck")
def healthcheck() -> HealthcheckResponse:
    return HealthcheckResponse(timestamp=int(time.time()))


@router.get("/status", summary="Services status")
async def status() -> StatusResponse:
    return StatusResponse()


@router.get("/version", summary="Application version")
async def get_version() -> VersionResponse:
    settings = get_settings()
    return VersionResponse(version=version(settings.APP_NAME))


# PROMETHEUS METRICS
def _verify_metrics_key(key: str = Header(default="")) -> None:
    """
    Optional security for metrics endpoint.
    Works ONLY if key configured.
    """
    settings = get_settings()
    print(settings.PROMETHEUS_METRICS_KEY)
    # if key not set -> public endpoint (for Prometheus scraping)
    if not settings.PROMETHEUS_METRICS_KEY:
        return

    if key != settings.PROMETHEUS_METRICS_KEY:
        raise HTTPException(status_code=403, detail="Forbidden metrics access")


@router.get("/metrics", summary="Prometheus metrics")
async def metrics(_: Annotated[None, Depends(_verify_metrics_key)]) -> Response:
    data = generate_latest(REGISTRY)
    return Response(data, media_type=CONTENT_TYPE_LATEST)
