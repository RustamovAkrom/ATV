from schemas.analytics.top import (
    TopAssetAnalyticsOut,
    TopMetric,
    TopServiceAnalyticsOut,
    TopUserAnalyticsOut,
)
from core.security.auth.types import CurrentUser
from db.models.enums import UserRole
from repositories.analytics.top_analytics_repo import TopAnalyticsRepository


class TopAnalyticsService:
    def __init__(self, repo: TopAnalyticsRepository):
        self.repo = repo

    @staticmethod
    def _pick_metric(row, metric: TopMetric) -> int:
        if metric == TopMetric.TRANSFERS:
            return int(row.transfer_count or 0)
        if metric == TopMetric.REPAIRS:
            return int(row.repair_count or 0)
        return int(row.assignment_count or 0)

    @staticmethod
    def _filter_email(email: str, current_user: CurrentUser) -> str:
        # Limit sensitive fields to privileged roles without changing the response schema.
        if current_user.has_role(UserRole.ADMIN.value, UserRole.SUPERADMIN.value):
            return email
        return ""

    async def get_top_assets(self, metric: TopMetric, limit: int):
        rows = await self.repo.get_top_assets(max(limit, 50))
        # Re-rank in memory because the selected leaderboard metric is runtime-driven.
        rows = sorted(
            rows,
            key=lambda row: (self._pick_metric(row, metric), str(row.id)),
            reverse=True,
        )
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

    async def get_top_users(self, metric: TopMetric, limit: int, current_user: CurrentUser):
        rows = await self.repo.get_top_users(max(limit, 50))
        rows = sorted(
            rows,
            key=lambda row: (self._pick_metric(row, metric), str(row.id)),
            reverse=True,
        )
        return [
            TopUserAnalyticsOut(
                user_id=row.id,
                user_name=row.full_name,
                email=self._filter_email(row.email, current_user),
                assignment_count=int(row.assignment_count or 0),
                transfer_count=int(row.transfer_count or 0),
                repair_count=int(row.repair_count or 0),
                primary_metric=metric,
                primary_value=self._pick_metric(row, metric),
            )
            for row in rows[:limit]
        ]

    async def get_top_services(self, metric: TopMetric, limit: int):
        rows = await self.repo.get_top_services(max(limit, 50))
        rows = sorted(
            rows,
            key=lambda row: (self._pick_metric(row, metric), str(row.id)),
            reverse=True,
        )
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
