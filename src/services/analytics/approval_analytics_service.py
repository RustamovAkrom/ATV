from repositories.analytics.approval_analytics_repo import ApprovalAnalyticsRepository
from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class ApprovalAnalyticsDomainService(BaseAnalyticsService):
    def __init__(self, repo: ApprovalAnalyticsRepository):
        self.repo = repo

    async def get(self, filters: AnalyticsFilters, user: CurrentUserSchema) -> dict:
        self.validate_filters(filters, user)
        row = await self.repo.metrics(filters.date_from, filters.date_to)

        decided = int(row.decided_count or 0)
        rejected = int(row.rejected_count or 0)

        return {
            "pending_approvals": int(row.pending_approvals or 0),
            "average_approval_time_hours": round(float(row.avg_approval_hours or 0), 2),
            "rejection_rate": round((rejected / decided * 100.0) if decided else 0.0, 2),
        }
