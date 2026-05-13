from repositories.analytics.transfer_analytics_repo import TransferAnalyticsRepository
from schemas.analytics.common import AnalyticsFilters, TimeSeriesPointSchema, TimeSeriesSchema
from schemas.auth import CurrentUserSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class TransferAnalyticsDomainService(BaseAnalyticsService):
    def __init__(self, repo: TransferAnalyticsRepository):
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
        points = [
            TimeSeriesPointSchema(period=r.period, value=int(r.transfer_count or 0))
            for r in raw["per_period"]
            if r.period is not None
        ]
        assets = [
            {
                "asset_id": str(r.asset_id),
                "asset_name": r.asset_name,
                "transfer_count": int(r.transfer_count or 0),
            }
            for r in raw["per_asset"]
        ]
        return {
            "transfers_per_period": TimeSeriesSchema(
                labels=[p.period.isoformat() for p in points],
                values=[p.value for p in points],
                points=points,
            ),
            "most_moved_assets": assets,
            "unstable_assets": [a for a in assets if a["transfer_count"] >= 3],
        }
