from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.approvals.approval_request import ApprovalRequest


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

    async def list(self) -> list[ApprovalRequest]:
        result = await self.session.execute(
            select(ApprovalRequest)
            .options(
                selectinload(ApprovalRequest.created_by),
                selectinload(ApprovalRequest.approved_by),
            )
            .order_by(ApprovalRequest.created_at.desc())
        )
        return result.scalars().all()

    async def flush(self) -> None:
        await self.session.flush()
