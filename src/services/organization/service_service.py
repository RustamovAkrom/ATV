from __future__ import annotations

from typing import Any
from uuid import UUID

from repositories.organization.service_repo import ServiceRepository
from schemas.organization.service import (
    ServiceCreateSchema,
    ServiceUpdateSchema,
    ServiceOutSchema,
    ServiceWithRegionsOutSchema,
)
from core.exceptions.errors import NotFound, Conflict, BadRequest
from db.models.org.service import Service
from utils.slug import slugify


class ServiceService:
    def __init__(self, repo: ServiceRepository):
        self.repo = repo

    async def list(self) -> list[ServiceOutSchema]:
        services = await self.repo.list()
        return [self._to_out_schema(s) for s in services]

    async def get(self, service_id: UUID) -> ServiceWithRegionsOutSchema:
        service = await self.repo.get(service_id)
        if not service:
            raise NotFound(f"Service {service_id} not found")
        return self._to_with_regions_schema(service)

    async def get_regions(self, service_id: UUID) -> list[dict[str, Any]]:
        service = await self.repo.get_regions(service_id)
        if not service:
            raise NotFound(f"Service {service_id} not found")

        regions = await self.repo.get_regions(service_id)
        return [
            {
                "id": r.id,
                "name": r.name,
                "parent_id": r.parent_id,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "geojson": r.geojson,
            }
            for r in regions
        ]

    async def create(self, data: ServiceCreateSchema) -> ServiceOutSchema:
        if await self.repo.check_name_exists(data.name):
            raise Conflict(f"Service with name '{data.name}' already exists ")

        print(data.model_dump(exclude_unset=True))
        service = await self.repo.create(
            {
                "name": data.name,
                "slug": slugify(data.name),
                "description": data.description if data.description else None,
            }

        )
        return self._to_out_schema(service)

    async def update(self, service_id: UUID, data: ServiceUpdateSchema) -> ServiceOutSchema:
        service = await self.repo.get(service_id)
        if not service:
            raise NotFound(f"Service {service_id} not found")

        if not data.name and not self.repo.check_name_exists(data.name, exclude_id=service_id):
            raise NotFound(f"Service with name '{data.name}' not found")

        update_data = {
                "name": data.name,
                "slug": slugify(data.name),
                "description": data.description if data.description else None,
        }

        updated = await self.repo.update(service_id, update_data)
        if not updated:
            raise BadRequest(f"Could not update service {service_id}")

        if data.region_ids:
            self.repo.set_regions(service.id, data.region_ids)

        return self._to_out_schema(updated)

    async def delete(self, service_id: UUID) -> dict[str, Any]:
        service = await self.repo.get(service_id)
        if not service:
            raise NotFound(f"Service {service_id} not found")

        await self.repo.delete(service_id)
        return {"message": "Service deleted successfully"}

    def _to_out_schema(self, service: Service) -> ServiceOutSchema:
        return ServiceOutSchema(
            id=service.id,
            name=service.name,
            slug=service.slug,
            description=service.description,
            created_at=service.created_at,
            updated_at=service.updated_at,
            region_ids=[r.id for r in service.regions] if service.regions else None,
        )

    def _to_with_regions_schema(self, service: Service) -> ServiceWithRegionsOutSchema:
        return ServiceWithRegionsOutSchema(
            id=service.id,
            name=service.name,
            description=service.description,
            created_at=service.created_at,
            updated_at=service.updated_at,
            region_ids=[r.id for r in service.regions] if service.regions else None,
            regions=[
                {
                    "id": r.id,
                    "name": r.name,
                    "parent_id": r.parent_id,
                }
                for r in service.regions
            ] if service.regions else None,
        )
