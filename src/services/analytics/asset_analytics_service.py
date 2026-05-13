from repositories.analytics.asset_analytics_repo import AssetAnalyticsRepository
from schemas.analytics.common import AnalyticsFilters
from schemas.auth import CurrentUserSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class AssetAnalyticsService(BaseAnalyticsService):
    def __init__(self, repo: AssetAnalyticsRepository):
        self.repo = repo

    async def distribution(self, filters: AnalyticsFilters, user: CurrentUserSchema) -> dict:
        self.validate_filters(filters, user)

        raw = await self.repo.distribution(
            filters.region_id,
            filters.service_id,
            user.assigned_region_id,
            user.assigned_service_id,
        )

        total = raw["total_assets"]

        return {
            "total_assets": total,
            "by_region": self.to_distribution(raw["by_region"], total, "id", "name"),
            "by_service": self.to_distribution(raw["by_service"], total, "id", "name"),
            "by_warehouse": self.to_distribution(raw["by_warehouse"], total, "id", "name"),
            "by_status": self.to_distribution(raw["by_status"], total, "status", "status"),
            "geo": [
                {
                    "region_id": str(r.region_id),
                    "region_name": r.region_name,
                    "metrics": {
                        "assets": int(r.asset_count or 0),
                        "critical": int(r.critical_assets_count or 0),
                        "repairs": 0,
                    },
                }
                for r in raw["geo"]
            ],
        }

    async def lifecycle(self, filters: AnalyticsFilters, user: CurrentUserSchema) -> dict:
        self.validate_filters(filters, user)

        raw = await self.repo.lifecycle(
            filters.region_id,
            filters.service_id,
            user.assigned_region_id,
            user.assigned_service_id,
        )

        total = raw["total"]
        items = [
            {
                "key": str(r.stage),
                "label": str(r.stage),
                "count": int(r.asset_count or 0),
                "percentage": round((int(r.asset_count or 0) / total * 100.0) if total else 0.0, 2),
            }
            for r in raw["rows"]
        ]

        return {
            "lifecycle_distribution": {
                "labels": [i["label"] for i in items],
                "values": [i["count"] for i in items],
                "items": items,
            },
            "critical_assets_percentage": round((raw["critical"] / total * 100.0) if total else 0.0, 2),
        }
