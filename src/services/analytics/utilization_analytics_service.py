from repositories.analytics.utilization_analytics_repo import (
    UtilizationAnalyticsRepository,
)
from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class UtilizationAnalyticsDomainService(BaseAnalyticsService):
    def __init__(self, repo: UtilizationAnalyticsRepository):
        self.repo = repo

    async def get(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        self.validate_filters(filters, user)
        raw = await self.repo.metrics(
            filters.region_id,
            filters.service_id,
            user.assigned_region_id,
            user.assigned_service_id,
        )
        loads = []
        ratios = []
        for row in raw["region_load"]:
            asset_count = int(row.asset_count or 0)
            employee_count = int(row.employee_count or 0)
            ratio = (
                (asset_count / employee_count) if employee_count else float(asset_count)
            )
            ratios.append(ratio)
            loads.append(
                {
                    "region_id": str(row.region_id),
                    "region_name": row.region_name,
                    "asset_count": asset_count,
                    "employee_count": employee_count,
                    "load_ratio": round(ratio, 2),
                }
            )
        avg = (sum(ratios) / len(ratios)) if ratios else 0.0
        return {
            "assets_per_employee": [
                {
                    "user_id": str(r.user_id),
                    "user_name": r.user_name,
                    "asset_count": int(r.asset_count or 0),
                }
                for r in raw["assets_per_employee"]
            ],
            "assets_per_service": [
                {
                    "service_id": str(r.service_id),
                    "service_name": r.service_name,
                    "asset_count": int(r.asset_count or 0),
                }
                for r in raw["assets_per_service"]
            ],
            "overloaded_regions": [x for x in loads if x["load_ratio"] > avg * 1.2],
            "underutilized_regions": [x for x in loads if x["load_ratio"] < avg * 0.8],
        }
