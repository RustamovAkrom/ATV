from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.org.region import Region
from repositories.base import BaseRepository
from core.exceptions.errors import Conflict


class RegionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[Region]:
        return await self.scalars(
            select(Region).order_by(Region.name)
        )

    async def get(self, region_id: UUID) -> Region | None:
        return await self.scalar(
            select(Region)
            .options(
                selectinload(Region.parent),
                selectinload(Region.children)
            )
            .where(Region.id == region_id)
        )

    async def create(self, data: dict) -> Region:
        region = Region(**data)
        self.add(region)
        await self.flush()
        await self.refresh(region)
        return region

    async def update(self, region_id: UUID, data: dict) -> Region | None:
        await self.execute(
            update(Region)
            .where(Region.id == region_id)
            .values(**data)
        )
        await self.flush()
        return await self.get(region_id)

    async def delete(self, region_id: UUID) -> bool:
        if await self.scalars_first(
            select(Region).where(Region.parent_id == region_id)
        ):
            raise Conflict("Cannot delete region with child regions")

        result = await self.execute(
            delete(Region).where(Region.id == region_id)
        )
        await self.flush()
        return result.rowcount > 0

    async def check_name_exists(self, name: str, exclude_id: UUID | None = None) -> bool:
        query = select(Region).where(Region.name == name)
        if exclude_id:
            query = query.where(Region.id != exclude_id)
        return await self.scalar(query) is not None

    async def get_children(self, region_id: UUID) -> list[Region]:
        return await self.scalars(
            select(Region).where(Region.parent_id == region_id)
        )

    async def build_tree(self) -> list[Region]:
        regions = await self.list()

        if not regions: return []

        region_map = {region.id: region for region in regions}
        root_regions = []

        for region in regions:
            region.children = []
            if region.parent_id and region.parent_id in region_map:
                parent = region_map[region.parent_id]
                if not hasattr(parent, '_children'):
                    parent._children = []
                parent._children.append(region)
            else:
                root_regions.append(region)

        for region in regions:
            if hasattr(region, '_children'):
                region.children = region._children

        return root_regions
