from __future__ import annotations

from datetime import date, datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import BaseRepository
from utils.analytics.date_utils import normalize_date_end, normalize_date_start
from utils.analytics.filter_utils import scoped_region_service_filters

T = TypeVar("T")


class BaseAnalyticsRepository(BaseRepository):
    """Base repository for analytics queries.

    The repository owns SQLAlchemy query helpers only: scope filters, date
    filters, count queries, and pagination. Domain-specific aggregation remains
    in specialized repositories.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def scope_filters(
        asset_table: Any,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> list:
        """Build SQLAlchemy filters for region/service scope."""
        return scoped_region_service_filters(
            asset_table,
            region_id=region_id,
            service_id=service_id,
            scoped_region_id=scoped_region_id,
            scoped_service_id=scoped_service_id,
        )

    @staticmethod
    def date_filters(
        table_column: Any,
        date_from: date | datetime | None = None,
        date_to: date | datetime | None = None,
    ) -> list:
        """Build SQLAlchemy filters for a date range."""
        filters = []
        normalized_from = normalize_date_start(date_from)
        normalized_to = normalize_date_end(date_to)
        if normalized_from:
            filters.append(table_column >= normalized_from)
        if normalized_to:
            filters.append(table_column <= normalized_to)
        return filters

    async def get_count(self, table: Any, filters: list | None = None) -> int:
        """Return the number of rows matching optional filters."""
        query = select(func.count(table.id))
        if filters:
            query = query.where(*filters)
        result = await self.session.scalar(query)
        return result or 0

    async def execute_with_pagination(
        self, query: Any, pagination: Any, order_by: Any | None = None
    ) -> tuple[Any, int]:
        """Execute a SQLAlchemy query and return the page plus total count."""
        if order_by is not None:
            query = query.order_by(order_by)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        query = query.limit(pagination.limit).offset(pagination.offset())
        result = await self.session.execute(query)

        return result, total
