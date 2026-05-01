from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload, selectinload

from db.models.assets.asset import Asset
from db.models.assets.asset_history import AssetHistory
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart
from db.models.users.permission import Role
from db.models.users.user import User
from repositories.base import BaseRepository


class RepairRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_asset(self, asset_id: UUID) -> Asset | None:
        return await self.scalar(
            select(Asset)
            .options(selectinload(Asset.repairs).selectinload(Repair.parts))
            .where(Asset.id == asset_id)
        )

    async def get_active_assignment(self, asset_id: UUID):
        return await self.scalar(
            select(Asset)
            .options(selectinload(Asset.assignments))
            .where(
                Asset.id == asset_id,
                Asset.assignments.any(lambda a: a.active.is_(True)),  # type: ignore
            )
        )

    async def get_asset_for_update(self, asset_id: UUID) -> Asset | None:
        return await self.scalar(
            select(Asset)
            .options(lazyload("*"))
            .where(Asset.id == asset_id)
            .with_for_update()
        )

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.scalar(
            select(User)
            .options(selectinload(User.role).selectinload(Role.permissions))
            .where(User.id == user_id)
        )

    async def get_repair(self, repair_id: UUID) -> Repair | None:
        return await self.scalar(
            select(Repair)
            .options(selectinload(Repair.parts))
            .where(Repair.id == repair_id)
        )

    async def get_repair_for_update(self, repair_id: UUID) -> Repair | None:
        return await self.scalar(
            select(Repair)
            .options(selectinload(Repair.parts))
            .where(Repair.id == repair_id)
            .with_for_update()
        )

    async def get_active_repair(self, asset_id: UUID) -> Repair | None:
        return await self.scalar(
            select(Repair)
            .options(selectinload(Repair.parts))
            .where(
                Repair.asset_id == asset_id,
                Repair.completed_at.is_(None),
            )
            .order_by(Repair.created_at.desc())
            .limit(1)
        )

    async def create_repair(self, repair: Repair) -> Repair:
        self.add(repair)
        await self.flush()
        return repair

    async def replace_parts(self, repair: Repair, parts: list[RepairPart]) -> Repair:
        repair.parts.clear()
        await self.flush()
        repair.parts.extend(parts)
        await self.flush()
        return repair

    async def add_history(
        self, asset_id: UUID, user_id: UUID, action: str, description: str
    ) -> AssetHistory:
        entry = AssetHistory(
            asset_id=asset_id,
            user_id=user_id,
            action=action,
            description=description,
        )
        self.add(entry)
        await self.flush()
        return entry
