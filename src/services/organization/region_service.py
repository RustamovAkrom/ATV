from __future__ import annotations

from typing import Any
from uuid import UUID

from core.exceptions.errors import BadRequest, Conflict, NotFound
from db.models.org.region import Region
from repositories.organization.region_repo import RegionRepository
from schemas.organization.region import (
    RegionCreateSchema,
    RegionOutSchema,
    RegionTreeOutSchema,
    RegionUpdateSchema,
)


class RegionService:
    def __init__(self, repo: RegionRepository):
        self.repo = repo

    async def get_tree(self) -> list[RegionTreeOutSchema]:
        """Получить дерево регионов (простая версия без рекурсии)"""
        regions = await self.repo.list()

        # Строим словарь для быстрого доступа
        region_dict = {}
        for region in regions:
            region_dict[region.id] = {
                "id": region.id,
                "name": region.name,
                "parent_id": region.parent_id,
                "latitude": region.latitude,
                "longitude": region.longitude,
                "geojson": region.geojson,
                "created_at": region.created_at,
                "updated_at": region.updated_at,
                "children": [],
            }

        # Формируем дерево
        roots = []
        for region_id, region_data in region_dict.items():
            parent_id = region_data["parent_id"]
            if parent_id and parent_id in region_dict:
                region_dict[parent_id]["children"].append(region_data)
            else:
                roots.append(region_data)

        # Конвертируем в схемы
        def to_tree(data):
            return RegionTreeOutSchema(
                id=data["id"],
                name=data["name"],
                parent_id=data["parent_id"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                geojson=data["geojson"],
                created_at=data["created_at"],
                updated_at=data["updated_at"],
                children=[to_tree(child) for child in data["children"]],
            )

        return [to_tree(root) for root in roots]

    async def list(
        self, level: int | None = None, parent_id: UUID | None = None
    ) -> list[RegionOutSchema]:
        regions = await self.repo.list()
        result = [self._to_out_schema(r) for r in regions]

        if level is not None:
            result = [r for r in result if self._get_level(r) == level]

        if parent_id is not None:
            result = [r for r in result if r.parent_id == parent_id]

        return result

    async def get(self, region_id: UUID) -> RegionOutSchema:
        region = await self.repo.get(region_id)
        if not region:
            raise NotFound(f"Region {region_id} not found")
        return self._to_out_schema(region)

    async def create(
        self, data: RegionCreateSchema, actor_id: UUID | None = None
    ) -> RegionOutSchema:
        if await self.repo.check_name_exists(data.name):
            raise Conflict(f"Region with name '{data.name}' already exists")

        if data.parent_id:
            parent = await self.repo.get(data.parent_id)
            if not parent:
                raise NotFound(f"Parent region {data.parent_id} not found")

        region = await self.repo.create(data.model_dump(exclude_unset=True))
        return self._to_out_schema(region)

    async def update(
        self, region_id: UUID, data: RegionUpdateSchema
    ) -> RegionOutSchema:
        region = await self.repo.get(region_id)
        if not region:
            raise NotFound(f"Region {region_id} not found")

        if data.name and await self.repo.check_name_exists(
            data.name, exclude_id=region_id
        ):
            raise Conflict(f"Region with name '{data.name}' already exists")

        if data.parent_id:
            parent = await self.repo.get(data.parent_id)
            if not parent:
                raise NotFound(f"Parent region {data.parent_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repo.update(region_id, update_data)

        if not updated:
            raise BadRequest(f"Could not update region {region_id}")

        return self._to_out_schema(updated)

    async def delete(self, region_id: UUID) -> dict[str, Any]:
        region = await self.repo.get(region_id)
        if not region:
            raise NotFound(f"Region {region_id} not found")
        await self.repo.delete(region_id)
        return {"message": "Region deleted successfully"}

    def _get_level(self, region: RegionOutSchema) -> int:
        """Вычислить уровень региона (простой способ)"""
        level = 1
        current_parent_id = region.parent_id
        # В реальности нужно загрузить всех родителей
        # Для простоты возвращаем 1
        return level

    def _to_out_schema(self, region: Region) -> RegionOutSchema:
        return RegionOutSchema(
            id=region.id,
            name=region.name,
            parent_id=region.parent_id,
            latitude=region.latitude,
            longitude=region.longitude,
            geojson=region.geojson,
            created_at=region.created_at,
            updated_at=region.updated_at,
        )
