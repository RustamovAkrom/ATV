from fastapi import APIRouter, Depends, Request
from core.security.rbac import presets
from core.cache.decorators import cached

from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.config import get_settings
from services.analytics.dashboard.top_assets_service import TopAssetsService
from api.dependencies.analytics import get_top_assets_service
from schemas.analytics.dashboard.top_assets import TopAssetOut

router = APIRouter(prefix="/top-assets")
settings = get_settings()
DASHBOARD_LIMIT, DASHBOARD_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS_DASHBOARD)


@router.get(
    "/",
    response_model=list[TopAssetOut],
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:dashboard:top-assets",))
async def get_top_assets(
    request: Request,
    service: TopAssetsService = Depends(get_top_assets_service),
):
    await enforce_rate_limit(request, "analytics:dashboard:top-assets", DASHBOARD_LIMIT, DASHBOARD_WINDOW)
    return await run_analytics_operation(request, "analytics.dashboard.top_assets", {}, lambda: service.get_top_assets(), lambda: [])
