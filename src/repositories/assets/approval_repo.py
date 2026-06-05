from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus
from repositories.base import BaseRepository
from schemas.pagination import PaginationParamsSchema


class ApprovalRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)

    async def create(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.add(approval)
        await self.flush()
        await self.refresh(approval)
        return approval

    async def get_pending_for(
        self,
        *,
        entity_type: str,
        entity_id: UUID,
        action: str,
    ) -> ApprovalRequest | None:
        return await self.scalar(
            select(ApprovalRequest).where(
                ApprovalRequest.entity_type == entity_type,
                ApprovalRequest.entity_id == entity_id,
                ApprovalRequest.action == action,
                ApprovalRequest.status == ApprovalStatus.PENDING,
                ApprovalRequest.executed.is_(False),
            )
        )

    async def get_by_id(self, approval_id: UUID) -> ApprovalRequest | None:
        return await self.scalar(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.created_by),
                selectinload(ApprovalRequest.approved_by),
            )
            .where(ApprovalRequest.id == approval_id)
        )

    async def get_by_id_for_update(self, approval_id: UUID) -> ApprovalRequest | None:
        return await self.scalar(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.created_by),
                selectinload(ApprovalRequest.approved_by),
            )
            .where(ApprovalRequest.id == approval_id)
            .with_for_update()
        )

    async def list(
        self,
        status: ApprovalStatus | None,
        pagination: PaginationParamsSchema,
    ) -> tuple[list[ApprovalRequest], int]:

        base = select(ApprovalRequest)

        if status:
            base = base.where(ApprovalRequest.status == status)

        total = await self.session.scalar(
            select(func.count()).select_from(base.subquery())
        )

        query = (
            base.options(
                selectinload(ApprovalRequest.created_by),
                selectinload(ApprovalRequest.approved_by),
            )
            .order_by(ApprovalRequest.created_at.desc())
            .limit(pagination.limit)
            .offset(pagination.offset())
        )

        result = await self.scalars(query)

        return result, int(total or 0)
