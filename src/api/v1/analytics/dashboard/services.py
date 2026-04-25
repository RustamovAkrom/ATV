from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_service_analytics_service
from api.v1.analytics._utils import (
    enforce_rate_limit,
    parse_rate_limit,
    run_analytics_operation,
)
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac import presets
from schemas.analytics.dashboard.services import ServiceBreakdownOut
from services.analytics.dashboard.service_service import ServiceAnalyticsService

router = APIRouter(prefix="/services")
settings = get_settings()
DASHBOARD_LIMIT, DASHBOARD_WINDOW = parse_rate_limit(
    settings.RATE_LIMIT_ANALYTICS_DASHBOARD
)


@router.get(
    "/",
    response_model=list[ServiceBreakdownOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=120, tags=("analytics:dashboard:services",))
async def get_service_breakdown(
    request: Request,
    service: ServiceAnalyticsService = Depends(get_service_analytics_service),
):
    await enforce_rate_limit(
        request, "analytics:dashboard:services", DASHBOARD_LIMIT, DASHBOARD_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.dashboard.services",
        {},
        lambda: service.get_breakdown(),
        lambda: [],
    )
