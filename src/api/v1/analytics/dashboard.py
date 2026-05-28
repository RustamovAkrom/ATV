from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import get_dashboard_analytics_service
from core.security.rbac.presets import AssetPermissions
from services.analytics.dashboard_analytics_service import DashboardAnalyticsService
from utils.analytics.cache_utils import run_analytics_operation

router = APIRouter(
    prefix="/analytics/dashboard",
    tags=["Analytics - Dashboard"],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)


@router.get("/overview/")
async def get_dashboard_overview(
    request: Request,
    service: DashboardAnalyticsService = Depends(get_dashboard_analytics_service),
):
    return await run_analytics_operation(
        request,
        "analytics.dashboard.overview",
        {},
        service.overview,
        service.empty_overview,
    )
