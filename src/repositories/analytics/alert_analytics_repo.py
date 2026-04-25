from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_transfer import AssetTransfer
from db.models.enums import AssetStatus, TransferStatus
from db.models.repairs.repair import Repair
from db.models.users.user import User


class AlertAnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def stuck_transfers(self, cutoff):
        result = await self.session.execute(
            select(AssetTransfer.id, Asset.name, AssetTransfer.created_at)
            .join(Asset, Asset.id == AssetTransfer.asset_id)
            .where(
                AssetTransfer.status == TransferStatus.PENDING,
                AssetTransfer.created_at <= cutoff,
            )
            .order_by(AssetTransfer.created_at.asc())
        )
        return result.all()

    async def excessive_repairs(self, since, threshold: int):
        result = await self.session.execute(
            select(
                Asset.id,
                Asset.name,
                func.count(Repair.id).label("repair_count"),
            )
            .join(Repair, Repair.asset_id == Asset.id)
            .where(Repair.created_at >= since)
            .group_by(Asset.id, Asset.name)
            .having(func.count(Repair.id) > threshold)
            .order_by(func.count(Repair.id).desc(), Asset.name.asc())
        )
        return result.all()

    async def inactive_assets(self, cutoff):
        active_assignment_exists = exists(
            select(AssetAssignment.id).where(
                AssetAssignment.asset_id == Asset.id,
                AssetAssignment.unassigned_at.is_(None),
            )
        )
        recent_transfer_exists = exists(
            select(AssetTransfer.id).where(
                AssetTransfer.asset_id == Asset.id,
                AssetTransfer.created_at >= cutoff,
            )
        )
        recent_repair_exists = exists(
            select(Repair.id).where(
                Repair.asset_id == Asset.id,
                Repair.created_at >= cutoff,
            )
        )
        result = await self.session.execute(
            select(Asset.id, Asset.name, Asset.updated_at)
            .where(
                Asset.status.in_([AssetStatus.ACTIVE, AssetStatus.ASSIGNED]),
                Asset.updated_at <= cutoff,
                ~active_assignment_exists,
                ~recent_transfer_exists,
                ~recent_repair_exists,
            )
            .order_by(Asset.updated_at.asc())
        )
        return result.all()

    async def overloaded_users(self, threshold: int):
        result = await self.session.execute(
            select(
                User.id,
                User.full_name,
                func.count(AssetAssignment.id).label("active_assignments"),
            )
            .join(AssetAssignment, AssetAssignment.user_id == User.id)
            .where(AssetAssignment.unassigned_at.is_(None))
            .group_by(User.id, User.full_name)
            .having(func.count(AssetAssignment.id) > threshold)
            .order_by(func.count(AssetAssignment.id).desc(), User.full_name.asc())
        )
        return result.all()

