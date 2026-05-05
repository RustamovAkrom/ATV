from __future__ import annotations

from typing import Any
from uuid import UUID

from repositories.organization.service_repo import ServiceRepository


class ServiceService:
    def __init__(self, repo: ServiceRepository):
        self.repo = repo

    async def list(self) -> list[dict[str, Any]]:
        return await self.repo.list()

    async def get(self, service_id: UUID) -> dict[str, Any] | None:
        return await self.repo.get(service_id)

    async def get_regions(self, service_id: UUID) -> list[dict[str, Any]]:
        return await self.repo.get_regions(service_id)
