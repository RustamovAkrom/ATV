from repositories.analytics.repair_analytics_repo import RepairAnalyticsRepository
from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class RepairAnalyticsDomainService(BaseAnalyticsService):
    def __init__(self, repo: RepairAnalyticsRepository):
        self.repo = repo

    async def get(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        self.validate_filters(filters, user)
        raw = await self.repo.metrics(
            filters.region_id,
            filters.service_id,
            filters.date_from,
            filters.date_to,
            user.assigned_region_id,
            user.assigned_service_id,
        )
        counts = [int(r.repair_count or 0) for r in raw["per_asset"]]
        avg_count = (sum(counts) / len(counts)) if counts else 0
        threshold = avg_count * 2 if avg_count else 0
        rows = [
            {
                "asset_id": str(r.asset_id),
                "asset_name": r.asset_name,
                "repair_count": int(r.repair_count or 0),
                "total_repair_cost": float(r.total_repair_cost or 0),
            }
            for r in raw["per_asset"]
        ]
        return {
            "average_repair_cost": round(raw["average_repair_cost"], 2),
            "per_asset": rows,
            "abnormal_repair_frequency_assets": [
                item
                for item in rows
                if item["repair_count"] >= threshold and threshold > 0
            ],
        }
