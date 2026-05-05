from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.org.region import Region
from db.models.org.service import Service, region_services
from repositories.base import BaseRepository


class ServiceRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[dict[str, Any]]:
        services = await self.scalars(select(Service).order_by(Service.name))
        return [self._to_dict(service) for service in services]

    async def get(self, service_id: UUID) -> dict[str, Any] | None:
        service = await self.scalar(select(Service).where(Service.id == service_id))
        if not service:
            return None
        return self._to_dict(service)

    async def get_regions(self, service_id: UUID) -> list[dict[str, Any]]:
        stmt = (
            select(Region)
            .join(region_services)
            .where(region_services.c.service_id == service_id)
            .order_by(Region.name)
        )
        regions = await self.scalars(stmt)
        return [
            {
                "id": region.id,
                "name": region.name,
                "parent_id": region.parent_id,
                "latitude": region.latitude,
                "longitude": region.longitude,
                "geojson": region.geojson,
            }
            for region in regions
        ]

    def _to_dict(self, service: Service) -> dict[str, Any]:
        return {
            "id": service.id,
            "name": service.name,
            "code": service.code,
            "description": service.description,
        }
