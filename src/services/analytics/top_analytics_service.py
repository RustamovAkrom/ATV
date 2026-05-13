from repositories.analytics.top_analytics_repo import TopAnalyticsRepository
from schemas.analytics.top import TopAssetAnalyticsOut, TopMetric, TopServiceAnalyticsOut, TopUserAnalyticsOut
from schemas.auth import CurrentUserSchema
from services.analytics.base_analytics_service import BaseAnalyticsService


class TopAnalyticsService(BaseAnalyticsService):
    def __init__(self, repo: TopAnalyticsRepository):
        self.repo = repo

    def _pick_metric(self, row, metric: TopMetric) -> int:
        if metric == TopMetric.TRANSFERS:
            return int(row.transfer_count or 0)
        if metric == TopMetric.REPAIRS:
            return int(row.repair_count or 0)
        return int(row.assignment_count or 0)

    async def get_top_assets(self, metric: TopMetric, limit: int) -> list[TopAssetAnalyticsOut]:
        rows = await self.repo.get_top_assets(max(limit, 50))
        rows = sorted(rows, key=lambda row: (self._pick_metric(row, metric), str(row.id)), reverse=True)

        return [
            TopAssetAnalyticsOut(
                asset_id=row.id,
                asset_name=row.name,
                asset_tag=row.asset_tag,
                assignment_count=int(row.assignment_count or 0),
                transfer_count=int(row.transfer_count or 0),
                repair_count=int(row.repair_count or 0),
                primary_metric=metric,
                primary_value=self._pick_metric(row, metric),
            )
            for row in rows[:limit]
        ]

    async def get_top_users(self, metric: TopMetric, limit: int, current_user: CurrentUserSchema) -> list[TopUserAnalyticsOut]:
        rows = await self.repo.get_top_users(max(limit, 50))
        rows = sorted(rows, key=lambda row: (self._pick_metric(row, metric), str(row.id)), reverse=True)

        return [
            TopUserAnalyticsOut(
                user_id=row.id,
                user_name=row.full_name,
                email=self.filter_email(row.email, current_user),
                assignment_count=int(row.assignment_count or 0),
                transfer_count=int(row.transfer_count or 0),
                repair_count=int(row.repair_count or 0),
                primary_metric=metric,
                primary_value=self._pick_metric(row, metric),
            )
            for row in rows[:limit]
        ]

    async def get_top_services(self, metric: TopMetric, limit: int) -> list[TopServiceAnalyticsOut]:
        rows = await self.repo.get_top_services(max(limit, 50))
        rows = sorted(rows, key=lambda row: (self._pick_metric(row, metric), str(row.id)), reverse=True)

        return [
            TopServiceAnalyticsOut(
                service_id=row.id,
                service_name=row.name,
                assignment_count=int(row.assignment_count or 0),
                transfer_count=int(row.transfer_count or 0),
                repair_count=int(row.repair_count or 0),
                primary_metric=metric,
                primary_value=self._pick_metric(row, metric),
            )
            for row in rows[:limit]
        ]
