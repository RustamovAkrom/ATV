import asyncio

from schemas.analytics.common import AnalyticsFilters, KPIResponseSchema
from schemas.auth import CurrentUserSchema
from services.analytics.approval_analytics_service import ApprovalAnalyticsDomainService
from services.analytics.asset_analytics_service import AssetAnalyticsService
from services.analytics.document_analytics_service import DocumentAnalyticsDomainService
from services.analytics.repair_analytics_service import RepairAnalyticsDomainService
from services.analytics.transfer_analytics_service import TransferAnalyticsDomainService
from services.analytics.utilization_analytics_service import (
    UtilizationAnalyticsDomainService,
)
from utils.helpers import utc_now


class ReportService:
    def __init__(
        self,
        asset_service: AssetAnalyticsService,
        repair_service: RepairAnalyticsDomainService,
        transfer_service: TransferAnalyticsDomainService,
        approval_service: ApprovalAnalyticsDomainService,
        document_service: DocumentAnalyticsDomainService,
        utilization_service: UtilizationAnalyticsDomainService,
    ):
        self.asset_service = asset_service
        self.repair_service = repair_service
        self.transfer_service = transfer_service
        self.approval_service = approval_service
        self.document_service = document_service
        self.utilization_service = utilization_service

    async def overview(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        assets, lifecycle, approvals = await asyncio.gather(
            self.asset_service.distribution(filters, user),
            self.asset_service.lifecycle(filters, user),
            self.approval_service.get(filters, user),
        )
        return {
            "kpis": [
                KPIResponseSchema(
                    key="total_assets",
                    label="Total Assets",
                    value=assets["total_assets"],
                ),
                KPIResponseSchema(
                    key="critical_lifecycle_pct",
                    label="Critical Lifecycle %",
                    value=lifecycle["critical_assets_percentage"],
                    unit="%",
                ),
                KPIResponseSchema(
                    key="pending_approvals",
                    label="Pending Approvals",
                    value=approvals["pending_approvals"],
                ),
                KPIResponseSchema(
                    key="rejection_rate",
                    label="Rejection Rate",
                    value=approvals["rejection_rate"],
                    unit="%",
                ),
            ],
            "breakdowns": {
                "assets_by_region": assets["by_region"],
                "assets_by_status": assets["by_status"],
            },
            "trends": {},
        }

    async def report(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        (
            summary,
            assets,
            repairs,
            documents,
            utilization,
            transfers,
            approvals,
        ) = await asyncio.gather(
            self.overview(filters, user),
            self.asset_service.distribution(filters, user),
            self.repair_service.get(filters, user),
            self.document_service.get(filters, user),
            self.utilization_service.get(filters, user),
            self.transfer_service.get(filters, user),
            self.approval_service.get(filters, user),
        )
        return {
            "version": "1.0",
            "generated_at": utc_now().isoformat(),
            "filters": filters.model_dump(mode="json"),
            "summary": summary,
            "breakdowns": {
                "assets": assets,
                "repairs": repairs,
                "documents": documents,
                "utilization": utilization,
            },
            "trends": {
                "transfers": transfers,
                "approvals": approvals,
            },
        }
