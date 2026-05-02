import asyncio

from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from services.analytics.approval_analytics_service import ApprovalAnalyticsDomainService
from services.analytics.asset_analytics_service import AssetAnalyticsService
from services.analytics.repair_analytics_service import RepairAnalyticsDomainService
from services.analytics.transfer_analytics_service import TransferAnalyticsDomainService


class DashboardService:
    def __init__(
        self,
        asset_service: AssetAnalyticsService,
        repair_service: RepairAnalyticsDomainService,
        transfer_service: TransferAnalyticsDomainService,
        approval_service: ApprovalAnalyticsDomainService,
    ):
        self.asset_service = asset_service
        self.repair_service = repair_service
        self.transfer_service = transfer_service
        self.approval_service = approval_service

    async def get(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        assets, lifecycle, repairs, transfers, approvals = await asyncio.gather(
            self.asset_service.distribution(filters, user),
            self.asset_service.lifecycle(filters, user),
            self.repair_service.get(filters, user),
            self.transfer_service.get(filters, user),
            self.approval_service.get(filters, user),
        )

        return {
            "kpis": [
                {"key": "total_assets", "value": assets["total_assets"]},
                {"key": "critical_pct", "value": lifecycle["critical_assets_percentage"]},
                {"key": "pending_approvals", "value": approvals["pending_approvals"]},
                {"key": "avg_repair_cost", "value": repairs["average_repair_cost"]},
            ],
            "charts": {
                "assets_by_region": assets["by_region"],
                "assets_by_status": assets["by_status"],
                "transfer_trend": transfers["transfers_per_period"],
            },
            "maps": {"regions": assets["geo"]},
        }
