from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.org.region import Region
from db.models.org.service import Service, region_services
from repositories.base import BaseRepository

from core.exceptions.errors import Conflict


class ServiceRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[Service]:
        return await self.scalars(
            select(Service).order_by(Service.name)
        )

    async def get(self, service_id: UUID) -> dict[str, Any] | None:
        return await self.scalar(
            select(Service)
            .options(
                selectinload(Service.regions)
            )
            .where(Service.id == service_id)
        )

    async def create(self, data: dict) -> Service:
        service = Service(**data)
        self.add(service)
        await self.flush()
        await self.flush(service)
        return service

    async def update(self, service_id: UUID, data: dict) -> Service | None:
        await self.execute(
            update(Service)
            .where(Service.id == service_id)
            .values(**data)
        )
        await self.flush()
        return await self.get(service_id)

    async def delete(self, service_id: UUID) -> bool:
        result = await self.execute(
            delete(Service).where(Service.id == service_id)
        )
        await self.flush()
        return result.rowcount > 0

    async def check_name_exists(self, name: str, exclude_id: UUID | None = None) -> bool:
        query = select(Service).where(Service.name == name)
        if exclude_id:
            query = query.where(Service.id != exclude_id)
        return await self.scalar(query) is not None

    async def get_regions(self, service_id: UUID) -> list[Region]:
        return await self.scalars(
            select(Region)
            .join(region_services)
            .where(region_services.c.service_id == service_id)
            .order_by(Region.name)
        )
