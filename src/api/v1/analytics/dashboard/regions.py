from fastapi import APIRouter, Depends, Request
from core.security.rbac import presets
from core.cache.decorators import cached

from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.config import get_settings
from services.analytics.dashboard.region_service import RegionAnalyticsService
from api.dependencies.analytics import get_region_analytics_service
from schemas.analytics.dashboard.region import RegionDistributionOut

router = APIRouter(prefix="/regions")
settings = get_settings()
DASHBOARD_LIMIT, DASHBOARD_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS_DASHBOARD)


@router.get(
    "/",
    response_model=list[RegionDistributionOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:dashboard:regions",))
async def get_regions(
    request: Request,
    service: RegionAnalyticsService = Depends(get_region_analytics_service),
):
    await enforce_rate_limit(request, "analytics:dashboard:regions", DASHBOARD_LIMIT, DASHBOARD_WINDOW)
    return await run_analytics_operation(request, "analytics.dashboard.regions", {}, lambda: service.get_region_distribution(), lambda: [])
