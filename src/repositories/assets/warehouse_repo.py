from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from db.models.assets.asset import Asset
from db.models.warehouse.warehouse import Warehouse
from repositories.base import BaseRepository


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
        """Get warehouse list with filtering and pagination"""
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

        return list(result.scalars().all()), total

    async def get(self, warehouse_id: UUID) -> Warehouse | None:
        """Get warehouse by ID with relations loaded"""
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
            update(Warehouse).where(Warehouse.id == warehouse_id).values(**data)
        )
        await self.flush()
        return await self.get(warehouse_id)

    async def delete(self, warehouse_id: UUID) -> bool:
        """Удалить склад"""
        result = await self.execute(
            delete(Warehouse).where(Warehouse.id == warehouse_id)
        )
        await self.flush()
        return self._rowcount(result) > 0

    async def check_slug_exists(
        self, slug: str, exclude_id: UUID | None = None
    ) -> bool:
        """Check if warehouse with this slug exists"""
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
            select(func.count(Asset.id)).where(
                Asset.current_warehouse_id == warehouse_id
            )
        )
        return result.scalar() or 0

    async def get_warehouse_with_assets(self, warehouse_id: UUID) -> Warehouse | None:
        """Get warehouse with assets"""
        result = await self.session.execute(
            select(Warehouse)
            .options(selectinload(Warehouse.assets))
            .where(Warehouse.id == warehouse_id)
        )
        return result.scalar_one_or_none()

    async def get_warehouse_stock(
        self, warehouse_id: UUID
    ) -> list[tuple[UUID, str, str | None, int, int, float]]:
        """Получить текущий остаток склада"""
        raise NotImplementedError(
            "Warehouse stock reporting is not implemented in WarehouseRepository"
        )

    async def record_stock_in(
        self,
        warehouse_id: UUID,
        part_id: UUID,
        quantity: int,
        reference_type: str,
        reference_id: UUID | None,
        moved_by: UUID,
    ) -> Any:
        """Записать поступление на склад"""
        raise NotImplementedError(
            "Warehouse stock movement is not implemented in WarehouseRepository"
        )

    async def record_stock_out(
        self,
        warehouse_id: UUID,
        part_id: UUID,
        quantity: int,
        reference_type: str,
        reference_id: UUID | None,
        moved_by: UUID,
    ) -> Any:
        """Record stock out from warehouse"""
        raise NotImplementedError(
            "Warehouse stock movement is not implemented in WarehouseRepository"
        )

    async def get_warehouse_movements(
        self,
        warehouse_id: UUID,
        movement_type: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Any], int]:
        """Получить движения по складу"""
        raise NotImplementedError(
            "Warehouse movements query is not implemented in WarehouseRepository"
        )

    async def get_part_movements(self, warehouse_id: UUID, part_id: UUID) -> list[Any]:
        """Получить движения по партии"""
        raise NotImplementedError(
            "Part movement query is not implemented in WarehouseRepository"
        )

    async def create_part(
        self,
        name: str,
        description: str | None = None,
        unit_price: Decimal | None = None,
    ) -> Any:
        """Создать партию/деталь"""
        raise NotImplementedError(
            "Warehouse part creation is not implemented in WarehouseRepository"
        )

    async def list_parts(
        self,
        warehouse_id: UUID | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[Any], int]:
        """Получить список партий/деталей"""
        raise NotImplementedError(
            "Warehouse part listing is not implemented in WarehouseRepository"
        )

    async def get_part_by_id(self, part_id: UUID) -> Any | None:
        """Получить деталь по ID"""
        raise NotImplementedError(
            "Warehouse part lookup is not implemented in WarehouseRepository"
        )

    async def update_part(self, part_id: UUID, data: dict[str, Any]) -> Any | None:
        """Обновить деталь"""
        raise NotImplementedError(
            "Warehouse part update is not implemented in WarehouseRepository"
        )

    async def delete_part(self, part_id: UUID) -> bool:
        """Удалить деталь"""
        raise NotImplementedError(
            "Warehouse part deletion is not implemented in WarehouseRepository"
        )
