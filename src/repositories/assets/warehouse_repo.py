from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from db.models.warehouse.warehouse import Warehouse
from db.models.assets.asset import Asset
from repositories.base import BaseRepository
from core.exceptions.errors import Conflict


class WarehouseRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        is_active: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Warehouse], int]:
        """Получить список складов с фильтрацией и пагинацией"""
        query = select(Warehouse)

        if region_id:
            query = query.where(Warehouse.region_id == region_id)
        if service_id:
            query = query.where(Warehouse.service_id == service_id)
        if is_active is not None:
            query = query.where(Warehouse.is_active == is_active)

        # Подсчет общего количества
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query) or 0

        # Пагинация
        query = query.order_by(Warehouse.name).offset(offset).limit(limit)
        result = await self.session.execute(query)

        return result.scalars().all(), total

    async def get(self, warehouse_id: UUID) -> Warehouse | None:
        """Получить склад по ID с загрузкой связей"""
        result = await self.session.execute(
            select(Warehouse)
            .options(
                joinedload(Warehouse.region),
                joinedload(Warehouse.service),
                joinedload(Warehouse.manager_user),
            )
            .where(Warehouse.id == warehouse_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Warehouse | None:
        """Получить склад по slug"""
        result = await self.session.execute(
            select(Warehouse).where(Warehouse.slug == slug)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> Warehouse:
        """Создать новый склад"""
        warehouse = Warehouse(**data)
        self.add(warehouse)
        await self.flush()
        await self.refresh(warehouse)
        return warehouse

    async def update(self, warehouse_id: UUID, data: dict) -> Warehouse | None:
        """Обновить склад"""
        await self.execute(
            update(Warehouse)
            .where(Warehouse.id == warehouse_id)
            .values(**data)
        )
        await self.flush()
        return await self.get(warehouse_id)

    async def delete(self, warehouse_id: UUID) -> bool:
        """Удалить склад"""
        result = await self.execute(
            delete(Warehouse).where(Warehouse.id == warehouse_id)
        )
        await self.flush()
        return result.rowcount > 0

    async def check_slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        """Проверить существование склада с таким slug"""
        if not slug:
            return False
        query = select(Warehouse).where(Warehouse.slug == slug)
        if exclude_id:
            query = query.where(Warehouse.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_assets_count(self, warehouse_id: UUID) -> int:
        """Получить количество активов на складе"""
        result = await self.session.execute(
            select(func.count(Asset.id)).where(Asset.current_warehouse_id == warehouse_id)
        )
        return result.scalar() or 0

    async def get_warehouse_with_assets(self, warehouse_id: UUID) -> Warehouse | None:
        """Получить склад с активами"""
        result = await self.session.execute(
            select(Warehouse)
            .options(selectinload(Warehouse.assets))
            .where(Warehouse.id == warehouse_id)
        )
        return result.scalar_one_or_none()
