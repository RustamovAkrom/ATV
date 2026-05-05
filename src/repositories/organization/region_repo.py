from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.org.region import Region
from db.models.org.service import region_services
from repositories.base import BaseRepository


class RegionRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self) -> list[dict[str, Any]]:
        regions = await self.scalars(select(Region).order_by(Region.name))
        results = [self._to_dict(region) for region in regions]
        self._hydrate_levels(results)
        return results

    async def get(self, region_id: UUID) -> Region | None:
        return await self.scalar(select(Region).where(Region.id == region_id))

    async def list_tree(self) -> list[dict[str, Any]]:
        nodes = await self.list()
        by_id = {node["id"]: {**node, "children": []} for node in nodes}
        tree: list[dict[str, Any]] = []

        for node in by_id.values():
            parent_id = node["parent_id"]
            if parent_id and parent_id in by_id:
                by_id[parent_id]["children"].append(node)
            else:
                tree.append(node)

        return tree

    async def get_regions_by_service(self, service_id: UUID) -> list[dict[str, Any]]:
        stmt = (
            select(Region)
            .join(region_services)
            .where(region_services.c.service_id == service_id)
            .order_by(Region.name)
        )
        regions = await self.scalars(stmt)
        results = [self._to_dict(region) for region in regions]
        self._hydrate_levels(results)
        return results

    def _to_dict(self, region: Region) -> dict[str, Any]:
        return {
            "id": region.id,
            "name": region.name,
            "parent_id": region.parent_id,
            "latitude": region.latitude,
            "longitude": region.longitude,
            "geojson": region.geojson,
        }

    def _hydrate_levels(self, regions: list[dict[str, Any]]) -> None:
        by_id = {region["id"]: region for region in regions}
        level_cache: dict[UUID, int] = {}

        def compute_level(region_id: UUID | None) -> int:
            if region_id is None:
                return 1
            if region_id in level_cache:
                return level_cache[region_id]
            region = by_id.get(region_id)
            if not region:
                return 1
            parent_level = compute_level(region["parent_id"])
            level = parent_level + 1 if region["parent_id"] else 1
            level_cache[region_id] = level
            return level

        for region in regions:
            region["level"] = compute_level(region["parent_id"]) if region["parent_id"] else 1
