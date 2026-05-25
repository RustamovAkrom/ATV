from fastapi import APIRouter, Depends, Request

from api.dependencies.analytics import (
    get_asset_assignment_analytics_service,
    get_asset_history_analytics_service,
    get_asset_transfer_analytics_service,
)
from api.v1.analytics._utils import run_analytics_operation
from core.security.rbac.presets import AssetPermissions
from schemas.analytics.asset_assignment_analytics import AssetAssignmentFilterInput
from schemas.analytics.asset_history import AssetHistoryFilter
from schemas.analytics.asset_transfer_analytics import AssetTransferFilterInput
from services.analytics.asset_assignment_analytics_service import (
    AssetAssignmentAnalyticsService,
)
from services.analytics.asset_history_analytics_service import (
    AssetHistoryAnalyticsService,
)
from services.analytics.asset_transfer_analytics_service import (
    AssetTransferAnalyticsService,
)

router = APIRouter(
    prefix="/analytics/dashboard",
    tags=["Analytics - Dashboard"],
    dependencies=[Depends(AssetPermissions.CanViewAssets)],
)


@router.get("/overview/")
async def get_dashboard_overview(
    request: Request,
    assignment_service: AssetAssignmentAnalyticsService = Depends(
        get_asset_assignment_analytics_service
    ),
    transfer_service: AssetTransferAnalyticsService = Depends(
        get_asset_transfer_analytics_service
    ),
    history_service: AssetHistoryAnalyticsService = Depends(
        get_asset_history_analytics_service
    ),
):
    async def _operation():
        assignment_metrics = await assignment_service.get_aggregates(
            AssetAssignmentFilterInput()
        )
        transfer_metrics = await transfer_service.get_transfer_metrics(
            AssetTransferFilterInput()
        )
        history_metrics = await history_service.get_aggregates(AssetHistoryFilter())

        return {
            "period": "all_time",
            "assignment_metrics": {
                "total_active": assignment_metrics.total_active_assignments,
                "total_inactive": assignment_metrics.total_inactive_assignments,
                "total_assignments": assignment_metrics.total_assignments,
            },
            "transfer_metrics": {
                "total_pending": transfer_metrics.pending_transfers,
                "total_transfers": transfer_metrics.total_transfers,
            },
            "asset_history_metrics": {
                "total_history_entries": history_metrics.total_entries,
                "unique_assets": history_metrics.unique_assets,
                "unique_users": history_metrics.unique_users,
            },
        }

    return await run_analytics_operation(
        request,
        "analytics.dashboard.overview",
        {},
        _operation,
        lambda: {
            "period": "all_time",
            "assignment_metrics": {
                "total_active": 0,
                "total_inactive": 0,
                "total_assignments": 0,
            },
            "transfer_metrics": {"total_pending": 0, "total_transfers": 0},
            "asset_history_metrics": {
                "total_history_entries": 0,
                "unique_assets": 0,
                "unique_users": 0,
            },
        },
    )
