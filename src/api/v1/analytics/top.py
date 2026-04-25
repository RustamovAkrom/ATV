from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import get_top_analytics_service
from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser
from core.cache.decorators import cached
from core.security.rbac import presets
from schemas.analytics.top import (
    TopAssetAnalyticsOut,
    TopMetric,
    TopServiceAnalyticsOut,
    TopUserAnalyticsOut,
)
from services.analytics.top_analytics_service import TopAnalyticsService

router = APIRouter(prefix="/analytics/top", tags=["Analytics - Top"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS)


@router.get("/assets", response_model=list[TopAssetAnalyticsOut], dependencies=[presets.CanViewAssets])
@cached(ttl=300, tags=("analytics:top:assets",))
async def get_top_assets(
    request: Request,
    metric: TopMetric = Query(default=TopMetric.ASSIGNMENTS),
    limit: int = Query(default=10, ge=1, le=100),
    service: TopAnalyticsService = Depends(get_top_analytics_service),
):
    await enforce_rate_limit(request, "analytics:top:assets", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.top.assets",
        {"metric": metric, "limit": limit},
        lambda: service.get_top_assets(metric, limit),
        lambda: [],
    )


@router.get("/users", response_model=list[TopUserAnalyticsOut], dependencies=[presets.CanViewAssets])
@cached(ttl=300, tags=("analytics:top:users",))
async def get_top_users(
    request: Request,
    metric: TopMetric = Query(default=TopMetric.ASSIGNMENTS),
    limit: int = Query(default=10, ge=1, le=100),
    service: TopAnalyticsService = Depends(get_top_analytics_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    await enforce_rate_limit(request, "analytics:top:users", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.top.users",
        {"metric": metric, "limit": limit},
        lambda: service.get_top_users(metric, limit, current_user),
        lambda: [],
    )


@router.get("/services", response_model=list[TopServiceAnalyticsOut], dependencies=[presets.CanViewAssets])
@cached(ttl=300, tags=("analytics:top:services",))
async def get_top_services(
    request: Request,
    metric: TopMetric = Query(default=TopMetric.ASSIGNMENTS),
    limit: int = Query(default=10, ge=1, le=100),
    service: TopAnalyticsService = Depends(get_top_analytics_service),
):
    await enforce_rate_limit(request, "analytics:top:services", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.top.services",
        {"metric": metric, "limit": limit},
        lambda: service.get_top_services(metric, limit),
        lambda: [],
    )
