from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import get_top_analytics_service
from core.cache.decorators import cached
from core.config import get_settings
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.top import (
    TopAssetAnalyticsOut,
    TopMetric,
    TopServiceAnalyticsOut,
    TopUserAnalyticsOut,
)
from schemas.auth import CurrentUserSchema
from services.analytics.top_analytics_service import TopAnalyticsService
from utils.analytics.cache_utils import run_analytics_operation

router = APIRouter(prefix="/analytics/top", tags=["Analytics - Top"])
settings = get_settings()


@router.get(
    "/assets",
    response_model=list[TopAssetAnalyticsOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:top:assets",))
async def get_top_assets(
    request: Request,
    metric: TopMetric = Query(TopMetric.ASSIGNMENTS),
    limit: int = Query(10, ge=1, le=100),
    service: TopAnalyticsService = Depends(get_top_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.top.assets",
        {"metric": metric, "limit": limit},
        lambda: service.get_top_assets(metric, limit),
        lambda: [],
    )


@router.get(
    "/users",
    response_model=list[TopUserAnalyticsOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:top:users",))
async def get_top_users(
    request: Request,
    metric: TopMetric = Query(TopMetric.ASSIGNMENTS),
    limit: int = Query(10, ge=1, le=100),
    service: TopAnalyticsService = Depends(get_top_analytics_service),
    current_user: CurrentUserSchema = Depends(get_current_user),
):
    return await run_analytics_operation(
        request,
        "analytics.top.users",
        {"metric": metric, "limit": limit},
        lambda: service.get_top_users(metric, limit, current_user),
        lambda: [],
    )


@router.get(
    "/services",
    response_model=list[TopServiceAnalyticsOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:top:services",))
async def get_top_services(
    request: Request,
    metric: TopMetric = Query(TopMetric.ASSIGNMENTS),
    limit: int = Query(10, ge=1, le=100),
    service: TopAnalyticsService = Depends(get_top_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.top.services",
        {"metric": metric, "limit": limit},
        lambda: service.get_top_services(metric, limit),
        lambda: [],
    )
