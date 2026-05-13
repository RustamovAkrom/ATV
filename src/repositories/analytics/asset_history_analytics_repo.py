from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.users.user import User
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository
from schemas.analytics.asset_history import AssetHistoryFilter
from schemas.pagination import PaginationParamsSchema


class AssetHistoryAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для аналитики истории активов"""

    def _apply_filters(self, query, filters: AssetHistoryFilter):
        """Применяет фильтры к запросу"""
        if not filters:
            return query

        if filters.asset_id:
            query = query.where(AssetHistory.asset_id == filters.asset_id)
        if filters.user_id:
            query = query.where(AssetHistory.user_id == filters.user_id)
        if filters.action:
            query = query.where(AssetHistory.action == filters.action)

        date_filters = self.date_filters(AssetHistory.created_at, filters.date_from, filters.date_to)
        query = query.where(*date_filters)

        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = query.join(Asset).join(User).where(
                or_(
                    Asset.name.ilike(term),
                    Asset.asset_tag.ilike(term),
                    User.full_name.ilike(term),
                    AssetHistory.description.ilike(term),
                    AssetHistory.action.ilike(term),
                )
            )

        return query

    async def list(
        self,
        filters: AssetHistoryFilter,
        pagination: PaginationParamsSchema
    ) -> tuple[list[AssetHistory], int]:
        """Список записей истории с пагинацией"""
        query = select(AssetHistory).options(
            selectinload(AssetHistory.asset),
            selectinload(AssetHistory.user),
        ).order_by(AssetHistory.created_at.desc())

        query = self._apply_filters(query, filters)
        result, total = await self.execute_with_pagination(query, pagination)

        return result.scalars().all(), total

    async def get_aggregates(self, filters: AssetHistoryFilter) -> dict:
        """Агрегированные метрики по истории"""
        base_query = select(AssetHistory.id)
        base_query = self._apply_filters(base_query, filters)
        filtered = base_query.subquery()

        # Основные агрегаты
        agg_query = select(
            func.count(filtered.c.id).label("total_entries"),
            func.count(func.distinct(AssetHistory.asset_id)).label("unique_assets"),
            func.count(func.distinct(AssetHistory.user_id)).label("unique_users"),
            func.min(AssetHistory.created_at).label("min_date"),
            func.max(AssetHistory.created_at).label("max_date"),
        ).select_from(filtered).join(AssetHistory, AssetHistory.id == filtered.c.id)

        aggregate_row = (await self.session.execute(agg_query)).one()

        # Разбивка по действиям
        actions_query = select(
            AssetHistory.action,
            func.count().label("count"),
            func.min(AssetHistory.created_at).label("first_occurrence"),
            func.max(AssetHistory.created_at).label("last_occurrence"),
        ).select_from(filtered).join(AssetHistory, AssetHistory.id == filtered.c.id).group_by(AssetHistory.action)

        actions_result = await self.session.execute(actions_query)
        actions_breakdown = [
            {
                "action": row[0],
                "count": row[1],
                "last_occurrence": row[2],
                "first_occurrence": row[3],
            }
            for row in actions_result.all()
        ]

        return {
            "total_entries": int(aggregate_row.total_entries or 0),
            "unique_assets": int(aggregate_row.unique_assets or 0),
            "unique_users": int(aggregate_row.unique_users or 0),
            "date_range_start": aggregate_row.min_date,
            "date_range_end": aggregate_row.max_date,
            "actions_breakdown": actions_breakdown,
        }
