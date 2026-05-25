from __future__ import annotations

from sqlalchemy import func, or_, select

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.users.user import User
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository
from schemas.analytics.asset_assignment_analytics import AssignmentAnalyticsStatus


class AssignmentBaseRepository(BaseAnalyticsRepository):
    """Базовый репозиторий для аналитики назначений"""

    def __init__(self, session):
        super().__init__(session)
        self.assignment_table = AssetAssignment
        self.asset_table = Asset
        self.user_table = User

    def apply_assignment_filters(self, query, filters, with_joins: bool = True):
        """Применяет фильтры к запросу назначений"""
        if not filters:
            return query

        if with_joins and hasattr(filters, "search") and filters.search:
            query = query.join(self.asset_table).join(self.user_table)

        if hasattr(filters, "asset_id") and filters.asset_id:
            query = query.where(self.assignment_table.asset_id == filters.asset_id)

        if hasattr(filters, "user_id") and filters.user_id:
            query = query.where(self.assignment_table.user_id == filters.user_id)

        if hasattr(filters, "status"):
            if filters.status == AssignmentAnalyticsStatus.ACTIVE:
                query = query.where(self.assignment_table.unassigned_at.is_(None))
            elif filters.status == AssignmentAnalyticsStatus.INACTIVE:
                query = query.where(self.assignment_table.unassigned_at.isnot(None))

        if hasattr(filters, "date_from") and filters.date_from:
            query = query.where(self.assignment_table.assigned_at >= filters.date_from)

        if hasattr(filters, "date_to") and filters.date_to:
            query = query.where(self.assignment_table.assigned_at <= filters.date_to)

        if hasattr(filters, "search") and filters.search and with_joins:
            term = f"%{filters.search.strip()}%"
            query = query.where(
                or_(
                    self.asset_table.name.ilike(term),
                    self.user_table.full_name.ilike(term),
                )
            )

        return query

    async def get_assignment_aggregates(self, filters) -> dict:
        """Получает агрегированные метрики для назначений"""
        # Базовый подзапрос с фильтрами
        base_query = select(self.assignment_table.id)
        base_query = self.apply_assignment_filters(
            base_query, filters, with_joins=False
        )
        filtered = base_query.subquery()

        aggregate_query = (
            select(
                func.count(filtered.c.id).label("total_assignments"),
                func.count(filtered.c.id)
                .filter(self.assignment_table.unassigned_at.is_(None))
                .label("active_assignments"),
                func.count(filtered.c.id)
                .filter(self.assignment_table.unassigned_at.isnot(None))
                .label("inactive_assignments"),
                func.avg(
                    self.assignment_table.unassigned_at
                    - self.assignment_table.assigned_at
                )
                .filter(self.assignment_table.unassigned_at.isnot(None))
                .label("avg_duration"),
            )
            .select_from(filtered)
            .join(self.assignment_table, self.assignment_table.id == filtered.c.id)
        )

        result = await self.session.execute(aggregate_query)
        row = result.one()

        return {
            "total_assignments": int(row.total_assignments or 0),
            "active_assignments": int(row.active_assignments or 0),
            "inactive_assignments": int(row.inactive_assignments or 0),
            "average_duration_days": self._interval_to_days(row.avg_duration),
        }

    @staticmethod
    def _interval_to_days(interval) -> float | None:
        """Конвертирует SQL interval в дни"""
        if interval is None:
            return None
        return (
            interval.total_seconds() / 86400
            if hasattr(interval, "total_seconds")
            else None
        )
