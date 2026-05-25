from __future__ import annotations

from datetime import date, datetime, time
from typing import TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.base import BaseRepository

T = TypeVar("T")


class BaseAnalyticsRepository(BaseRepository):
    """Базовый репозиторий для аналитики с общими методами"""

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def scope_filters(
        asset_table,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        scoped_region_id: UUID | None = None,
        scoped_service_id: UUID | None = None,
    ) -> list:
        """Создает фильтры по региону и сервису с учетом скоупа"""
        filters = []
        if scoped_region_id or region_id:
            target_region_id = scoped_region_id or region_id
            if target_region_id:
                filters.append(asset_table.region_id == target_region_id)
        if scoped_service_id or service_id:
            target_service_id = scoped_service_id or service_id
            if target_service_id:
                filters.append(asset_table.service_id == target_service_id)
        return filters

    @staticmethod
    def date_filters(
        table_column,
        date_from: date | datetime | None = None,
        date_to: date | datetime | None = None,
    ) -> list:
        """Создает фильтры по дате"""
        filters = []
        if date_from:
            if isinstance(date_from, date) and not isinstance(date_from, datetime):
                date_from = datetime.combine(date_from, time.min)
            filters.append(table_column >= date_from)
        if date_to:
            if isinstance(date_to, date) and not isinstance(date_to, datetime):
                date_to = datetime.combine(date_to, time.max)
            filters.append(table_column <= date_to)
        return filters

    async def get_count(self, table, filters: list = None) -> int:
        """Получает количество записей с фильтрами"""
        query = select(func.count(table.id))
        if filters:
            query = query.where(*filters)
        result = await self.session.scalar(query)
        return result or 0

    async def execute_with_pagination(self, query, pagination, order_by=None):
        """Выполняет запрос с пагинацией"""
        if order_by:
            query = query.order_by(order_by)

        # Считаем общее количество
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Пагинация
        query = query.limit(pagination.limit).offset(pagination.offset())
        result = await self.session.execute(query)

        return result, total
