from typing import Any

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
from services.analytics.base_analytics_service import BaseAnalyticsService


class DashboardAnalyticsService(BaseAnalyticsService):
    """Build high-level dashboard metrics from specialized analytics services."""

    def __init__(
        self,
        assignment_service: AssetAssignmentAnalyticsService,
        transfer_service: AssetTransferAnalyticsService,
        history_service: AssetHistoryAnalyticsService,
    ) -> None:
        self.assignment_service = assignment_service
        self.transfer_service = transfer_service
        self.history_service = history_service

    async def overview(self) -> dict[str, Any]:
        """Return KPI blocks for the main analytics dashboard."""
        assignment_metrics = await self.assignment_service.get_aggregates(
            AssetAssignmentFilterInput()
        )
        transfer_metrics = await self.transfer_service.get_transfer_metrics(
            AssetTransferFilterInput()
        )
        history_metrics = await self.history_service.get_aggregates(
            AssetHistoryFilter()
        )

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

    @staticmethod
    def empty_overview() -> dict[str, Any]:
        """Return the stable empty dashboard payload used as a fallback."""
        return {
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
        }
