from __future__ import annotations

from typing import Any
from uuid import UUID

from repositories.organization.region_repo import RegionRepository
from schemas.organization.region import (
    RegionCreateSchema,
    RegionUpdateSchema,
    RegionOutSchema,
    RegionTreeOutSchema,
)
from core.exceptions.errors import NotFound, Conflict, BadRequest
from db.models.org.region import Region


class RegionService:
    def __init__(self, repo: RegionRepository):
        self.repo = repo

    async def get_tree(self) -> list[RegionTreeOutSchema]:
        roots = await self.repo.build_tree()
        return [self._to_tree_schema(root) for root in roots]

    async def list(
        self,
        level: int | None = None,
        parent_id: UUID | None = None
    ) -> list[RegionOutSchema]:

        regions = await self.repo.list()

        # convert into schemas
        result = [self._to_out_schema(r) for r in regions]

        # Filter for levels
        if level is not None:
            result = [r for r in result if r.level == level]

        if parent_id is not None:
            result = [r for r in result if r.parent_id == parent_id]

        return result

    async def get(self, region_id: UUID) -> dict[str, Any] | None:
        region = await self.repo.get(region_id)
        if not region:
            raise NotFound(f"Region {region_id} not found")

        return self._to_out_schema(region)

    async def create(
        self,
        data: RegionCreateSchema,
        actor_id: UUID | None = None
    ) -> RegionOutSchema:
        # check for unique
        if await self.repo.check_name_exists(data.name):
            raise Conflict(f"Region with name '{data.name}' already exists")

        if data.parent_id:
            parent = await self.repo.get(data.parent_id)
            if not parent:
                raise NotFound(f"Parent region {data.parent_id} not found")

        region = await self.repo.create(data.model_dump(exclude_unset=True))
        return self._to_out_schema(region)

    async def update(
        self,
        region_id: UUID,
        data: RegionUpdateSchema
    ) -> RegionOutSchema:
        region = await self.repo.get(region_id)
        if not region:
            raise NotFound(f"Region {region_id} not found")

        if data.name and await self.repo.check_name_exists(data.name, exclude_id=region_id):
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

    def _calculate_level(self, region, all_regions: dict[UUID, RegionOutSchema]) -> int:
        """Вычислить уровень региона в иерархии"""
        level = 1
        current = region
        while current.parent_id:
            level += 1
            current = all_regions.get(current.parent_id)
            if not current:
                break
        return level

    def _to_out_schema(self, region: Region) -> RegionOutSchema:
        """Конвертировать модель в схему"""
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

    def _to_tree_schema(self, region: Region) -> RegionTreeOutSchema:
        """Рекурсивно конвертировать модель в древовидную схему"""
        return RegionTreeOutSchema(
            id=region.id,
            name=region.name,
            parent_id=region.parent_id,
            latitude=region.latitude,
            longitude=region.longitude,
            geojson=region.geojson,
            created_at=region.created_at,
            updated_at=region.updated_at,
            children=[self._to_tree_schema(child) for child in getattr(region, 'children', [])]
        )
