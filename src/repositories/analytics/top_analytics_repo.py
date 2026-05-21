from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_transfer import AssetTransfer
from db.models.org.service import Service
from db.models.repairs.repair import Repair
from db.models.users.user import User
from repositories.analytics.base_analytics_repo import BaseAnalyticsRepository


class TopAnalyticsRepository(BaseAnalyticsRepository):
    """Репозиторий для топ-аналитики"""

    async def get_top_assets(self, limit: int = 10):
        """Топ активов по активности"""
        assignments = (
            select(
                AssetAssignment.asset_id.label("asset_id"),
                func.count(AssetAssignment.id).label("assignment_count"),
            )
            .group_by(AssetAssignment.asset_id)
            .subquery()
        )

        transfers = (
            select(
                AssetTransfer.asset_id.label("asset_id"),
                func.count(AssetTransfer.id).label("transfer_count"),
            )
            .group_by(AssetTransfer.asset_id)
            .subquery()
        )

        repairs = (
            select(
                Repair.asset_id.label("asset_id"),
                func.count(Repair.id).label("repair_count"),
            )
            .group_by(Repair.asset_id)
            .subquery()
        )

        query = select(
            Asset.id,
            Asset.name,
            func.coalesce(assignments.c.assignment_count, 0).label("assignment_count"),
            func.coalesce(transfers.c.transfer_count, 0).label("transfer_count"),
            func.coalesce(repairs.c.repair_count, 0).label("repair_count"),
        ).outerjoin(assignments, assignments.c.asset_id == Asset.id).outerjoin(
            transfers, transfers.c.asset_id == Asset.id
        ).outerjoin(repairs, repairs.c.asset_id == Asset.id).order_by(
            func.coalesce(assignments.c.assignment_count, 0).desc(),
            func.coalesce(transfers.c.transfer_count, 0).desc(),
            func.coalesce(repairs.c.repair_count, 0).desc(),
            Asset.name.asc(),
        ).limit(limit)

        result = await self.session.execute(query)
        return result.all()

    async def get_top_users(self, limit: int = 10):
        """Топ пользователей по активности"""
        assignments = (
            select(
                AssetAssignment.user_id.label("user_id"),
                func.count(AssetAssignment.id).label("assignment_count"),
            )
            .group_by(AssetAssignment.user_id)
            .subquery()
        )

        transfers = (
            select(
                AssetTransfer.created_by_id.label("user_id"),
                func.count(AssetTransfer.id).label("transfer_count"),
            )
            .group_by(AssetTransfer.created_by_id)
            .subquery()
        )

        repairs = (
            select(
                Repair.reported_by_id.label("user_id"),
                func.count(Repair.id).label("repair_count"),
            )
            .where(Repair.reported_by_id.isnot(None))
            .group_by(Repair.reported_by_id)
            .subquery()
        )

        query = select(
            User.id,
            User.full_name,
            User.email,
            func.coalesce(assignments.c.assignment_count, 0).label("assignment_count"),
            func.coalesce(transfers.c.transfer_count, 0).label("transfer_count"),
            func.coalesce(repairs.c.repair_count, 0).label("repair_count"),
        ).outerjoin(assignments, assignments.c.user_id == User.id).outerjoin(
            transfers, transfers.c.user_id == User.id
        ).outerjoin(repairs, repairs.c.user_id == User.id).order_by(
            func.coalesce(assignments.c.assignment_count, 0).desc(),
            func.coalesce(transfers.c.transfer_count, 0).desc(),
            func.coalesce(repairs.c.repair_count, 0).desc(),
            User.full_name.asc(),
        ).limit(limit)

        result = await self.session.execute(query)
        return result.all()

    async def get_top_services(self, limit: int = 10):
        """Топ сервисов по активности"""
        assignments = (
            select(
                Asset.service_id.label("service_id"),
                func.count(AssetAssignment.id).label("assignment_count"),
            )
            .join(AssetAssignment, AssetAssignment.asset_id == Asset.id)
            .where(Asset.service_id.isnot(None))
            .group_by(Asset.service_id)
            .subquery()
        )

        transfer_events = (
            select(AssetTransfer.from_service_id.label("service_id"))
            .where(AssetTransfer.from_service_id.isnot(None))
            .union_all(
                select(AssetTransfer.to_service_id.label("service_id")).where(
                    AssetTransfer.to_service_id.isnot(None)
                )
            )
            .subquery()
        )

        transfers = (
            select(
                transfer_events.c.service_id,
                func.count().label("transfer_count"),
            )
            .group_by(transfer_events.c.service_id)
            .subquery()
        )

        repairs = (
            select(
                Asset.service_id.label("service_id"),
                func.count(Repair.id).label("repair_count"),
            )
            .join(Repair, Repair.asset_id == Asset.id)
            .where(Asset.service_id.isnot(None))
            .group_by(Asset.service_id)
            .subquery()
        )

        query = select(
            Service.id,
            Service.name,
            func.coalesce(assignments.c.assignment_count, 0).label("assignment_count"),
            func.coalesce(transfers.c.transfer_count, 0).label("transfer_count"),
            func.coalesce(repairs.c.repair_count, 0).label("repair_count"),
        ).outerjoin(assignments, assignments.c.service_id == Service.id).outerjoin(
            transfers, transfers.c.service_id == Service.id
        ).outerjoin(repairs, repairs.c.service_id == Service.id).order_by(
            func.coalesce(assignments.c.assignment_count, 0).desc(),
            func.coalesce(transfers.c.transfer_count, 0).desc(),
            func.coalesce(repairs.c.repair_count, 0).desc(),
            Service.name.asc(),
        ).limit(limit)

        result = await self.session.execute(query)
        return result.all()
