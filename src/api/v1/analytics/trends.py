from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import get_trend_analytics_service
from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.trends import RepairTrendSeriesOut, TrendInterval, TrendSeriesOut
from services.analytics.trend_analytics_service import TrendAnalyticsService

router = APIRouter(prefix="/analytics/trends", tags=["Analytics - Trends"])
settings = get_settings()
ANALYTICS_LIMIT, ANALYTICS_WINDOW = parse_rate_limit("5/minute")


@router.get("/assignments", response_model=TrendSeriesOut, dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=300, tags=("analytics:trends:assignments",))
async def get_assignment_trends(
    request: Request, interval: TrendInterval = Query(TrendInterval.DAILY), periods: int = Query(30, ge=1, le=180),
    service: TrendAnalyticsService = Depends(get_trend_analytics_service),
):
    await enforce_rate_limit(request, "analytics:trends:assignments", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request, "analytics.trends.assignments", {"interval": interval, "periods": periods},
        lambda: service.assignment_trends(interval, periods),
        lambda: TrendSeriesOut(interval=interval, points=[]),
    )


@router.get("/transfers", response_model=TrendSeriesOut, dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=300, tags=("analytics:trends:transfers",))
async def get_transfer_trends(
    request: Request, interval: TrendInterval = Query(TrendInterval.DAILY), periods: int = Query(30, ge=1, le=180),
    service: TrendAnalyticsService = Depends(get_trend_analytics_service),
):
    await enforce_rate_limit(request, "analytics:trends:transfers", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request, "analytics.trends.transfers", {"interval": interval, "periods": periods},
        lambda: service.transfer_trends(interval, periods),
        lambda: TrendSeriesOut(interval=interval, points=[]),
    )


@router.get("/repairs", response_model=RepairTrendSeriesOut, dependencies=[Depends(AssetPermissions.CanViewAssets)])
@cached(ttl=300, tags=("analytics:trends:repairs",))
async def get_repair_trends(
    request: Request, interval: TrendInterval = Query(TrendInterval.DAILY), periods: int = Query(30, ge=1, le=180),
    service: TrendAnalyticsService = Depends(get_trend_analytics_service),
):
    await enforce_rate_limit(request, "analytics:trends:repairs", ANALYTICS_LIMIT, ANALYTICS_WINDOW)
    return await run_analytics_operation(
        request, "analytics.trends.repairs", {"interval": interval, "periods": periods},
        lambda: service.repair_trends(interval, periods),
        lambda: RepairTrendSeriesOut(interval=interval, points=[]),
    )
