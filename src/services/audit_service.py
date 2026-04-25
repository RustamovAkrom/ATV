from uuid import UUID

from core.audit.stream import audit_stream
from db.models.audit.audit_log import AuditLog
from repositories.audit_repo import AuditRepository
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

    @staticmethod
    def _to_schema(item: AuditLog) -> AuditSchema:
        return AuditSchema.model_validate(item, from_attributes=True)

    @staticmethod
    def _make_page(
        items: list[AuditLog], total: int, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        return PageSchema[AuditSchema](
            items=[
                AuditSchema.model_validate(item, from_attributes=True) for item in items
            ],
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def persist_audit(self, data: AuditCreateSchema | dict) -> AuditSchema:
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
        return self._make_page(items, total, pagination)

    async def get_recent(
        self, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_recent(pagination.limit, pagination.offset())
        return self._make_page(items, total, pagination)

    async def get_by_request_id(
        self, request_id: str, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_by_request_id(
            request_id, pagination.limit, pagination.offset()
        )
        return self._make_page(items, total, pagination)

    async def get_by_user(
        self, user_id: UUID, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_by_user(
            user_id, pagination.limit, pagination.offset()
        )
        return self._make_page(items, total, pagination)

    async def get_by_status_code(
        self, status_code: int, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_by_status_code(
            status_code, pagination.limit, pagination.offset()
        )
        return self._make_page(items, total, pagination)

    async def get_errors(
        self, pagination: PaginationParamsSchema
    ) -> PageSchema[AuditSchema]:
        items, total = await self.repo.get_errors(pagination.limit, pagination.offset())
        return self._make_page(items, total, pagination)

    async def get_stats(self) -> AuditStatsSchema:
        stats = await self.repo.get_stats()
        return AuditStatsSchema(**stats)

    async def publish_stream(self, event: dict) -> None:
        await audit_stream.publish(event)
