from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.exceptions.errors import Conflict
from db.models.org.region import Region
from repositories.base import BaseRepository


class RegionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[Region]:
        """Получить все регионы (без детей)"""
        result = await self.session.execute(select(Region).order_by(Region.name))
        return result.scalars().all()

    async def get(self, region_id: UUID) -> Region | None:
        """Получить регион по ID"""
        result = await self.session.execute(
            select(Region).where(Region.id == region_id)
        )
        return result.scalar_one_or_none()

    async def get_with_children(self, region_id: UUID) -> Region | None:
        """Получить регион с детьми"""
        result = await self.session.execute(
            select(Region)
            .options(selectinload(Region.children))
            .where(Region.id == region_id)
        )
        return result.scalar_one_or_none()

    async def get_root_regions(self) -> list[Region]:
        """Получить корневые регионы (без родителей)"""
        result = await self.session.execute(
            select(Region).where(Region.parent_id.is_(None)).order_by(Region.name)
        )
        return result.scalars().all()

    async def create(self, data: dict) -> Region:
        region = Region(**data)
        self.add(region)
        await self.flush()
        await self.refresh(region)
        return region

    async def update(self, region_id: UUID, data: dict) -> Region | None:
        await self.execute(update(Region).where(Region.id == region_id).values(**data))
        await self.flush()
        return await self.get(region_id)

    async def delete(self, region_id: UUID) -> bool:
        # Проверка на наличие дочерних регионов
        result = await self.session.execute(
            select(Region).where(Region.parent_id == region_id)
        )
        if result.scalars().first():
            raise Conflict("Cannot delete region with child regions")

        result = await self.execute(delete(Region).where(Region.id == region_id))
        await self.flush()
        return result.rowcount > 0

    async def check_name_exists(
        self, name: str, exclude_id: UUID | None = None
    ) -> bool:
        query = select(Region).where(Region.name == name)
        if exclude_id:
            query = query.where(Region.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_children(self, region_id: UUID) -> list[Region]:
        result = await self.session.execute(
            select(Region).where(Region.parent_id == region_id)
        )
        return result.scalars().all()
