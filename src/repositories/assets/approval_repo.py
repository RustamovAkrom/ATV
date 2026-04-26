from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus

from schemas.pagination import PaginationParamsSchema


class ApprovalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.session.add(approval)
        await self.session.flush()
        return approval

    async def get_by_id(self, approval_id: UUID) -> ApprovalRequest | None:
        result = await self.session.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.created_by),
                selectinload(ApprovalRequest.approved_by),
            )
            .where(ApprovalRequest.id == approval_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_update(self, approval_id: UUID) -> ApprovalRequest | None:
        result = await self.session.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.created_by),
                selectinload(ApprovalRequest.approved_by),
            )
            .where(ApprovalRequest.id == approval_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        status: ApprovalStatus | None,
        pagination: PaginationParamsSchema,
    ) -> list[ApprovalRequest]:

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

        result = await self.session.execute(query)

        return result.scalars().all(), int(total or 0)

    async def flush(self) -> None:
        await self.session.flush()
