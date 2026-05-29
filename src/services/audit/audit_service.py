from typing import Any
from uuid import UUID

from pydantic import BaseModel

from core.audit.stream import audit_stream
from core.config import get_settings
from db.models.audit.audit_log import AuditLog
from repositories.audit.audit_repo import AuditRepository
from schemas.audit import (
    AuditCreateSchema,
    AuditFiltersSchema,
    AuditSchema,
    AuditStatsSchema,
)
from schemas.pagination import PageSchema, PaginationParamsSchema


class AuditService:
    def __init__(self, repo: AuditRepository):
        self.repo = repo
        self._settings = get_settings()

    def _is_enabled(self) -> bool:
        return self._settings.AUDIT_ENABLED

    @staticmethod
    def _to_schema(item: AuditLog) -> AuditSchema:
        return AuditSchema.model_validate(item, from_attributes=True)

    def _paginate(
        self,
        items: list[AuditLog],
        total: int,
        pagination: PaginationParamsSchema,
    ) -> PageSchema[AuditSchema]:
        return PageSchema[AuditSchema](
            items=[self._to_schema(item) for item in items],
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def persist_audit(
        self, data: AuditCreateSchema | dict[str, Any]
    ) -> AuditSchema:
        if isinstance(data, BaseModel):
            data = data.model_dump()
        audit = await self.repo.create(data)
        return self._to_schema(audit)

    async def list_audit_logs(
        self,
        filters: AuditFiltersSchema | None,
        pagination: PaginationParamsSchema,
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.list(
            filters, pagination.limit, pagination.offset()
        )
        return self._paginate(items, total, pagination)

    async def get_recent(
        self, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_recent(pagination.limit, pagination.offset())
        return self._paginate(items, total, pagination)

    async def get_by_request_id(
        self, request_id: str, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_by_request_id(
            request_id, pagination.limit, pagination.offset()
        )
        return self._paginate(items, total, pagination)

    async def get_by_user(
        self, user_id: UUID, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_by_user(
            user_id, pagination.limit, pagination.offset()
        )
        return self._paginate(items, total, pagination)

    async def get_by_status_code(
        self, status_code: int, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_by_status_code(
            status_code, pagination.limit, pagination.offset()
        )
        return self._paginate(items, total, pagination)

    async def get_errors(
        self, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_errors(pagination.limit, pagination.offset())
        return self._paginate(items, total, pagination)

    async def get_stats(self) -> AuditStatsSchema:
        stats = await self.repo.get_stats()
        return AuditStatsSchema(**(stats or {}))

    async def publish_stream(self, event: dict) -> None:
        if not self._is_enabled():
            return
        await audit_stream.publish(event)
