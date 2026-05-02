from __future__ import annotations

from repositories.analytics.asset_analytics_repo import AssetAnalyticsRepository
from schemas.analytics.common import (
    AggregationResultSchema,
    AnalyticsFilters,
    DistributionSchema,
)
from schemas.auth import CurrentUserSchema
from services.analytics._scope import validate_filters


class AssetAnalyticsService:
    def __init__(self, repo: AssetAnalyticsRepository):
        self.repo = repo

    @staticmethod
    def _to_distribution(rows, total: int) -> DistributionSchema:
        items = []
        for row in rows:
            count = int(row.asset_count or 0)
            label = str(getattr(row, "name", None) or getattr(row, "status", "Unknown"))
            key = str(getattr(row, "id", None) or getattr(row, "status", "unknown"))
            items.append(
                AggregationResultSchema(
                    key=key,
                    label=label,
                    count=count,
                    percentage=round((count / total * 100.0) if total else 0.0, 2),
                )
            )
        return DistributionSchema(
            labels=[i.label for i in items], values=[i.count for i in items], items=items
        )

    async def distribution(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        validate_filters(filters, user)
        raw = await self.repo.distribution(
            filters.region_id,
            filters.service_id,
            user.assigned_region_id,
            user.assigned_service_id,
        )
        total = raw["total_assets"]
        return {
            "total_assets": total,
            "by_region": self._to_distribution(raw["by_region"], total),
            "by_service": self._to_distribution(raw["by_service"], total),
            "by_warehouse": self._to_distribution(raw["by_warehouse"], total),
            "by_status": self._to_distribution(raw["by_status"], total),
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

    async def lifecycle(self, filters: AnalyticsFilters, user: CurrentUserSchema):
        validate_filters(filters, user)
        raw = await self.repo.lifecycle(
            filters.region_id,
            filters.service_id,
            user.assigned_region_id,
            user.assigned_service_id,
        )
        total = raw["total"]
        items = [
            AggregationResultSchema(
                key=str(r.stage),
                label=str(r.stage),
                count=int(r.asset_count or 0),
                percentage=round((int(r.asset_count or 0) / total * 100.0) if total else 0.0, 2),
            )
            for r in raw["rows"]
        ]
        return {
            "lifecycle_distribution": DistributionSchema(
                labels=[i.label for i in items],
                values=[i.count for i in items],
                items=items,
            ),
            "critical_assets_percentage": round(
                (raw["critical"] / total * 100.0) if total else 0.0, 2
            ),
        }
