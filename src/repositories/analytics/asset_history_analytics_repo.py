# repositories/analytics/asset_history_analytics_repo.py

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.users.user import User
from schemas.analytics.asset_history import AssetHistoryFilter
from schemas.pagination import PaginationParamsSchema


class AssetHistoryAnalyticsRepository:
    """Read-optimized repository for asset history analytics."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _apply_filters(self, query, filters: AssetHistoryFilter):
        """Apply filters to query."""
        filters = filters or AssetHistoryFilter()

        if filters.asset_id:
            query = query.where(AssetHistory.asset_id == filters.asset_id)

        if filters.user_id:
            query = query.where(AssetHistory.user_id == filters.user_id)

        if filters.action:
            query = query.where(AssetHistory.action == filters.action)

        if filters.date_from:
            query = query.where(AssetHistory.created_at >= filters.date_from)

        if filters.date_to:
            query = query.where(AssetHistory.created_at <= filters.date_to)

        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = (
                query.join(Asset)
                .join(User)
                .where(
                    or_(
                        Asset.name.ilike(term),
                        Asset.asset_tag.ilike(term),
                        User.full_name.ilike(term),
                        AssetHistory.description.ilike(term),
                        AssetHistory.action.ilike(term),
                    )
                )
            )

        return query

    def _build_filtered_subquery(self, filters: AssetHistoryFilter):
        return self._apply_filters(
            select(AssetHistory.id).select_from(AssetHistory),
            filters,
        ).subquery()

    async def list(
        self, filters: AssetHistoryFilter, pagination: PaginationParamsSchema
    ) -> tuple[list[AssetHistory], int]:
        """List history entries with pagination."""
        query = (
            select(AssetHistory)
            .options(
                selectinload(AssetHistory.asset),
                selectinload(AssetHistory.user),
            )
            .order_by(AssetHistory.created_at.desc())
        )

        query = self._apply_filters(query, filters)

        # Count total
        count_query = select(func.count(AssetHistory.id)).select_from(AssetHistory)
        count_query = self._apply_filters(count_query, filters)
        total = await self.session.scalar(count_query)

        result = await self.session.execute(
            query.limit(pagination.limit).offset(pagination.offset())
        )

        return result.scalars().all(), int(total or 0)

    async def get_aggregates(self, filters: AssetHistoryFilter) -> dict:
        """Get aggregated metrics."""
        filtered = self._build_filtered_subquery(filters)
        aggregate_row = (
            await self.session.execute(
                select(
                    func.count(filtered.c.id).label("total_entries"),
                    func.count(func.distinct(AssetHistory.asset_id)).label(
                        "unique_assets"
                    ),
                    func.count(func.distinct(AssetHistory.user_id)).label(
                        "unique_users"
                    ),
                    func.min(AssetHistory.created_at).label("min_date"),
                    func.max(AssetHistory.created_at).label("max_date"),
                )
                .select_from(filtered)
                .join(AssetHistory, AssetHistory.id == filtered.c.id)
            )
        ).one()

        # Actions breakdown
        actions_result = await self.session.execute(
            select(
                AssetHistory.action,
                func.count().label("count"),
                func.min(AssetHistory.created_at).label("first_occurrence"),
                func.max(AssetHistory.created_at).label("last_occurrence"),
            )
            .select_from(filtered)
            .join(AssetHistory, AssetHistory.id == filtered.c.id)
            .group_by(AssetHistory.action)
        )

        actions_breakdown = [
            {
                "action": row[0],
                "count": row[1],
                "last_occurrence": row[2],
                "first_occurrence": row[3],
            }
            for row in actions_result.all()
        ]

        # Most active asset
        most_active_asset = await self._get_most_active_asset(filtered)

        # Most active user
        most_active_user = await self._get_most_active_user(filtered)

        return {
            "total_entries": int(aggregate_row.total_entries or 0),
            "unique_assets": int(aggregate_row.unique_assets or 0),
            "unique_users": int(aggregate_row.unique_users or 0),
            "date_range_start": aggregate_row.min_date,
            "date_range_end": aggregate_row.max_date,
            "actions_breakdown": actions_breakdown,
            "most_active_asset_id": most_active_asset[0] if most_active_asset else None,
            "most_active_asset_name": (
                most_active_asset[1] if most_active_asset else None
            ),
            "most_active_user_id": most_active_user[0] if most_active_user else None,
            "most_active_user_name": most_active_user[1] if most_active_user else None,
        }

    async def _get_most_active_asset(self, filtered) -> tuple[UUID, str] | None:
        """Get the most frequently appearing asset in history."""
        result = await self.session.execute(
            select(Asset.id, Asset.name)
            .select_from(filtered)
            .join(AssetHistory, AssetHistory.id == filtered.c.id)
            .join(Asset, Asset.id == AssetHistory.asset_id)
            .group_by(Asset.id, Asset.name)
            .order_by(func.count(AssetHistory.id).desc())
            .limit(1)
        )
        row = result.first()
        return (row[0], row[1]) if row else None

    async def _get_most_active_user(self, filtered) -> tuple[UUID, str] | None:
        """Get the user with most history entries."""
        result = await self.session.execute(
            select(User.id, User.full_name)
            .select_from(filtered)
            .join(AssetHistory, AssetHistory.id == filtered.c.id)
            .join(User, User.id == AssetHistory.user_id)
            .group_by(User.id, User.full_name)
            .order_by(func.count(AssetHistory.id).desc())
            .limit(1)
        )
        row = result.first()
        return (row[0], row[1]) if row else None
