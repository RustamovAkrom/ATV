from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from db.models.approvals.approval_request import ApprovalRequest
from db.models.enums import ApprovalStatus

from schemas.pagination import PaginationParamsSchema
from core.exceptions.errors import Conflict
from repositories.base import BaseRepository


class ApprovalRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, approval: ApprovalRequest) -> ApprovalRequest:
        self.add(approval)
        await self.flush()
        return approval

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

        result = await self.scalars(query)

        return result, int(total or 0)
