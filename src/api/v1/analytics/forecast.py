from fastapi import APIRouter, Depends, Query, Request

from api.dependencies.analytics import get_forecast_analytics_service
from api.v1.analytics._utils import run_analytics_operation
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.forecast import ForecastSeriesOut
from schemas.analytics.trends import TrendInterval
from services.analytics.forecast_analytics_service import ForecastAnalyticsService

router = APIRouter(prefix="/analytics/forecast", tags=["Analytics - Forecast"])
settings = get_settings()


@router.get(
    "/repairs",
    response_model=ForecastSeriesOut,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:forecast:repairs",))
async def get_repair_forecast(
    request: Request,
    interval: TrendInterval = Query(TrendInterval.WEEKLY),
    periods: int = Query(8, ge=1, le=52),
    basis_window: int = Query(4, ge=1, le=24),
    service: ForecastAnalyticsService = Depends(get_forecast_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.forecast.repairs",
        {"interval": interval, "periods": periods, "basis_window": basis_window},
        lambda: service.repair_forecast(interval, periods, basis_window),
        lambda: ForecastSeriesOut(
            interval=interval,
            basis_window=basis_window,
            forecast_periods=periods,
            moving_average=0,
            points=[],
        ),
    )


@router.get(
    "/failures",
    response_model=ForecastSeriesOut,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=300, tags=("analytics:forecast:failures",))
async def get_failure_forecast(
    request: Request,
    interval: TrendInterval = Query(TrendInterval.WEEKLY),
    periods: int = Query(8, ge=1, le=52),
    basis_window: int = Query(4, ge=1, le=24),
    service: ForecastAnalyticsService = Depends(get_forecast_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.forecast.failures",
        {"interval": interval, "periods": periods, "basis_window": basis_window},
        lambda: service.failure_forecast(interval, periods, basis_window),
        lambda: ForecastSeriesOut(
            interval=interval,
            basis_window=basis_window,
            forecast_periods=periods,
            moving_average=0,
            points=[],
        ),
    )
