from decimal import Decimal
from fastapi import APIRouter, Depends, Request
from core.security.rbac import presets
from core.cache.decorators import cached

from api.v1.analytics._utils import enforce_rate_limit, parse_rate_limit, run_analytics_operation
from core.config import get_settings
from services.analytics.dashboard.overview_service import OverviewService
from api.dependencies.analytics import get_overview_service
from schemas.analytics.dashboard.overview import DashboardOverviewOut
from utils.helpers import utc_now

router = APIRouter(prefix="/overview")
settings = get_settings()
DASHBOARD_LIMIT, DASHBOARD_WINDOW = parse_rate_limit(settings.RATE_LIMIT_ANALYTICS_DASHBOARD)


@router.get(
    "/",
    response_model=DashboardOverviewOut,
    dependencies=[presets.CanViewAssets],
)
@cached(ttl=300, tags=("analytics:dashboard:overview",))
async def get_overview(
    request: Request,
    service: OverviewService = Depends(get_overview_service),
):
    await enforce_rate_limit(request, "analytics:dashboard:overview", DASHBOARD_LIMIT, DASHBOARD_WINDOW)
    return await run_analytics_operation(
        request,
        "analytics.dashboard.overview",
        {},
        lambda: service.get(),
        lambda: DashboardOverviewOut(
            timestamp=utc_now(),
            period="all_time",
            assignment_metrics={"total_active": 0, "total_inactive": 0, "average_duration_days": Decimal(0)},
            transfer_metrics={"total_pending": 0, "total_completed": 0, "average_completion_days": Decimal(0), "critical_bottlenecks": 0},
            asset_history_metrics={"total_history_entries": 0, "most_active_asset_id": None, "most_active_asset_name": None, "last_history_entry_date": None},
            total_assets_with_active_assignments=0,
            total_users_with_active_assignments=0,
            total_assets_in_transfer=0,
        ),
    )
