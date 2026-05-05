from __future__ import annotations

from typing import Any
from uuid import UUID

from repositories.organization.region_repo import RegionRepository


class RegionService:
    def __init__(self, repo: RegionRepository):
        self.repo = repo

    async def get_tree(self) -> list[dict[str, Any]]:
        return await self.repo.list_tree()

    async def list(self, level: int | None = None, parent_id: UUID | None = None) -> list[dict[str, Any]]:
        regions = await self.repo.list()
        if level is not None:
            regions = [region for region in regions if region.get("level") == level]
        if parent_id is not None:
            regions = [region for region in regions if region.get("parent_id") == parent_id]
        return regions

    async def get(self, region_id: UUID) -> dict[str, Any] | None:
        region = await self.repo.get(region_id)
        if not region:
            return None
        return {
            "id": region.id,
            "name": region.name,
            "parent_id": region.parent_id,
            "latitude": region.latitude,
            "longitude": region.longitude,
            "geojson": region.geojson,
        }
