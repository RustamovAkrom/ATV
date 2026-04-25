from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_history import AssetHistory
from db.models.users.permission import Role
from db.models.users.user import User


class AssetAssignmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        result = await self.session.execute(
            select(Asset)
            .options(
                selectinload(Asset.owner),
                selectinload(Asset.assignments).selectinload(AssetAssignment.user),
            )
            .where(Asset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def get_asset_plain(self, asset_id: UUID) -> Asset | None:
        result = await self.session.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()

    async def get_asset_for_update(self, asset_id: UUID, nowait: bool = False):
        stmt = (
            select(Asset.id).where(Asset.id == asset_id).with_for_update(nowait=nowait)
        )

        result = await self.session.execute(stmt)
        row = result.first()

        if not row:
            return None

        # второй запрос БЕЗ lock
        return await self.get_asset_plain(asset_id)

    async def get_user(self, user_id: UUID) -> User | None:
        result = await self.session.execute(
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_active_assignment(self, asset_id: UUID) -> AssetAssignment | None:
        result = await self.session.execute(
            select(AssetAssignment)
            .where(
                AssetAssignment.asset_id == asset_id,
                AssetAssignment.unassigned_at.is_(None),
            )
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_assignment(self, asset_id: UUID, user_id: UUID) -> AssetAssignment:
        assignment = AssetAssignment(asset_id=asset_id, user_id=user_id)
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def close_assignment(
        self, assignment: AssetAssignment, timestamp: datetime
    ) -> AssetAssignment:
        assignment.unassigned_at = timestamp
        await self.session.flush()
        return assignment

    async def add_history(
        self, asset_id: UUID, user_id: UUID, action: str, description: str
    ) -> AssetHistory:
        entry = AssetHistory(
            asset_id=asset_id,
            user_id=user_id,
            action=action,
            description=description,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def flush(self) -> None:
        await self.session.flush()
