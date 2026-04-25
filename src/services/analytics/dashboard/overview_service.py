from schemas.analytics.dashboard.overview import (
    DashboardOverviewOut,
    AssignmentMetricsCard,
    TransferMetricsCard,
    AssetHistoryMetricsCard,
)

from services.analytics.asset_assignment_analytics_service import (
    AssetAssignmentAnalyticsService,
)
from services.analytics.asset_transfer_analytics_service import (
    AssetTransferAnalyticsService,
)
from services.analytics.asset_history_analytics_service import (
    AssetHistoryAnalyticsService,
)
from utils.helpers import utc_now


class OverviewService:
    def __init__(
        self,
        assignment_analytics: AssetAssignmentAnalyticsService,
        transfer_analytics: AssetTransferAnalyticsService,
        history_analytics: AssetHistoryAnalyticsService,
    ):
        self.assignment_analytics = assignment_analytics
        self.transfer_analytics = transfer_analytics
        self.history_analytics = history_analytics

    async def get(self) -> DashboardOverviewOut:
        assignment = await self.assignment_analytics.get_aggregates(None)
        transfer = await self.transfer_analytics.get_transfer_metrics(None)
        history = await self.history_analytics.get_aggregates(None)

        return DashboardOverviewOut(
            timestamp=utc_now(),
            period="all_time",

            assignment_metrics=AssignmentMetricsCard(
                total_active=assignment.total_active_assignments,
                total_inactive=assignment.total_inactive_assignments,
                average_duration_days=assignment.average_assignment_duration_days,
            ),

            transfer_metrics=TransferMetricsCard(
                total_pending=transfer.pending_transfers,
                total_completed=transfer.completed_transfers,
                average_completion_days=transfer.average_completion_time_days,
                critical_bottlenecks=transfer.transfers_pending_over_30_days,
            ),

            asset_history_metrics=AssetHistoryMetricsCard(
                total_history_entries=history.total_entries,
                most_active_asset_id=history.most_active_asset_id,
                most_active_asset_name=history.most_active_asset_name,
                last_history_entry_date=history.date_range_end,
            ),

            total_assets_with_active_assignments=assignment.total_active_assignments,
            total_users_with_active_assignments=history.unique_users,
            total_assets_in_transfer=transfer.pending_transfers,
        )
