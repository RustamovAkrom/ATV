from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_repair_analytics_service
from api.v1.analytics._utils import (
    enforce_rate_limit,
    parse_rate_limit,
    run_analytics_operation,
)
from core.cache.decorators import cached
from core.config import get_settings
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.dashboard.repairs import RepairOut, RepairSummaryOut
from services.analytics.dashboard.repair_service import RepairAnalyticsService

router = APIRouter(prefix="/repairs")
settings = get_settings()
DASHBOARD_LIMIT, DASHBOARD_WINDOW = parse_rate_limit(
    settings.RATE_LIMIT_ANALYTICS_DASHBOARD
)


@router.get(
    "/recent",
    response_model=list[RepairOut],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=60, tags=("analytics:dashboard:repairs",))
async def get_recent_repairs(
    request: Request,
    service: RepairAnalyticsService = Depends(get_repair_analytics_service),
):
    await enforce_rate_limit(
        request, "analytics:dashboard:repairs:recent", DASHBOARD_LIMIT, DASHBOARD_WINDOW
    )
    return await run_analytics_operation(
        request,
        "analytics.dashboard.repairs.recent",
        {},
        lambda: service.get_recent(),
        lambda: [],
    )


@router.get(
    "/summary",
    response_model=RepairSummaryOut,
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)
@cached(ttl=120, tags=("analytics:dashboard:repairs:summary",))
async def get_repairs_summary(
    request: Request,
    service: RepairAnalyticsService = Depends(get_repair_analytics_service),
):
    await enforce_rate_limit(
        request,
        "analytics:dashboard:repairs:summary",
        DASHBOARD_LIMIT,
        DASHBOARD_WINDOW,
    )
    return await run_analytics_operation(
        request,
        "analytics.dashboard.repairs.summary",
        {},
        lambda: service.get_summary(),
        lambda: RepairSummaryOut(
            total_repairs=0, active_repairs=0, completed_repairs=0
        ),
    )
