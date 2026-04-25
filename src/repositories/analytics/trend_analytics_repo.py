from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_transfer import AssetTransfer
from db.models.repairs.repair import Repair
from db.models.repairs.repair_part import RepairPart


class TrendAnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _bucket(interval: str, column):
        if interval == "weekly":
            return func.date_trunc("week", column)
        if interval == "monthly":
            return func.date_trunc("month", column)
        return func.date_trunc("day", column)

    async def assignment_counts(self, interval: str, start: datetime, end: datetime):
        bucket = self._bucket(interval, AssetAssignment.assigned_at)
        result = await self.session.execute(
            select(
                bucket.label("bucket_start"),
                func.count(AssetAssignment.id).label("value"),
            )
            .where(
                AssetAssignment.assigned_at >= start, AssetAssignment.assigned_at <= end
            )
            .group_by(bucket)
            .order_by(bucket.asc())
        )
        return result.all()

    async def transfer_counts(self, interval: str, start: datetime, end: datetime):
        bucket = self._bucket(interval, AssetTransfer.created_at)
        result = await self.session.execute(
            select(
                bucket.label("bucket_start"),
                func.count(AssetTransfer.id).label("value"),
            )
            .where(AssetTransfer.created_at >= start, AssetTransfer.created_at <= end)
            .group_by(bucket)
            .order_by(bucket.asc())
        )
        return result.all()

    async def repair_counts(self, interval: str, start: datetime, end: datetime):
        repair_parts = (
            select(
                RepairPart.repair_id.label("repair_id"),
                func.sum(RepairPart.quantity * RepairPart.unit_price).label(
                    "parts_cost"
                ),
            )
            .group_by(RepairPart.repair_id)
            .subquery()
        )
        bucket = self._bucket(interval, Repair.created_at)
        result = await self.session.execute(
            select(
                bucket.label("bucket_start"),
                func.count(Repair.id).label("value"),
                func.coalesce(
                    func.sum(
                        func.coalesce(Repair.labor_cost, 0)
                        + func.coalesce(repair_parts.c.parts_cost, 0)
                    ),
                    0,
                ).label("total_cost"),
            )
            .outerjoin(repair_parts, repair_parts.c.repair_id == Repair.id)
            .where(Repair.created_at >= start, Repair.created_at <= end)
            .group_by(bucket)
            .order_by(bucket.asc())
        )
        return result.all()
