from __future__ import annotations

from typing import Any
from uuid import UUID

from core.exceptions.errors import BadRequest, Conflict, NotFound
from db.models.org.service import Service
from repositories.organization.service_repo import ServiceRepository
from schemas.organization.service import (
    ServiceCreateSchema,
    ServiceOutSchema,
    ServiceUpdateSchema,
    ServiceWithRegionsOutSchema,
)
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
        """Получить регионы для сервиса"""
        service = await self.repo.get(service_id)
        if not service:
            raise NotFound(f"Service {service_id} not found")

        regions = await self.repo.get_regions(service_id)
        return [
            {
                "id": str(r.id),
                "name": r.name,
                "parent_id": str(r.parent_id) if r.parent_id else None,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "geojson": r.geojson,
            }
            for r in regions
        ]

    async def create(self, data: ServiceCreateSchema) -> ServiceOutSchema:
        """Создать новый сервис"""
        # Проверка уникальности имени
        if await self.repo.check_name_exists(data.name):
            raise Conflict(f"Service with name '{data.name}' already exists")

        # Создаём сервис
        service = await self.repo.create(
            {
                "name": data.name,
                "slug": slugify(data.name),
                "description": data.description if data.description else None,
            }
        )

        # Привязываем регионы (если переданы)
        if data.region_ids:
            try:
                await self.repo.set_regions(service.id, data.region_ids)
            except Conflict as e:
                # Если ошибка с регионами, удаляем созданный сервис
                await self.repo.delete(service.id)
                raise Conflict(str(e))
            except Exception as e:
                await self.repo.delete(service.id)
                raise BadRequest(f"Failed to attach regions: {str(e)}")

        return await self.get(service.id)

    async def update(
        self, service_id: UUID, data: ServiceUpdateSchema
    ) -> ServiceOutSchema:
        """Обновить сервис"""
        service = await self.repo.get(service_id)
        if not service:
            raise NotFound(f"Service {service_id} not found")

        update_data = {}

        if data.name is not None:
            # Проверка уникальности имени
            if await self.repo.check_name_exists(data.name, exclude_id=service_id):
                raise Conflict(f"Service with name '{data.name}' already exists")
            update_data["name"] = data.name
            update_data["slug"] = slugify(data.name)

        if data.description is not None:
            update_data["description"] = data.description

        if update_data:
            updated = await self.repo.update(service_id, update_data)
            if not updated:
                raise BadRequest(f"Could not update service {service_id}")
            service = updated

        # Обновляем привязку регионов (если переданы)
        if data.region_ids is not None:
            await self.repo.set_regions(service_id, data.region_ids)

        return await self.get(service_id)

    async def delete(self, service_id: UUID) -> dict[str, Any]:
        """Удалить сервис"""
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
            slug=service.slug,
            description=service.description,
            created_at=service.created_at,
            updated_at=service.updated_at,
            region_ids=[r.id for r in service.regions] if service.regions else None,
            regions=[
                {
                    "id": str(r.id),
                    "name": r.name,
                    "parent_id": str(r.parent_id) if r.parent_id else None,
                }
                for r in service.regions
            ]
            if service.regions
            else None,
        )
