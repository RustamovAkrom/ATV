from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from db.models.enums import RepairStatus
from db.models.repairs.repair import Repair


class RepairAnalyticsRepository:
    def __init__(self, session):
        self.session = session

    async def get_recent_repairs(self, limit: int = 10):
        result = await self.session.execute(
            select(Repair)
            .options(selectinload(Repair.asset))  # 🔥 avoid N+1
            .order_by(Repair.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()

    async def get_summary(self):
        result = await self.session.execute(
            select(
                func.count(Repair.id).label("total"),
                func.count()
                .filter(Repair.status == RepairStatus.IN_PROGRESS)
                .label("active"),
                func.count()
                .filter(Repair.status == RepairStatus.DONE)
                .label("completed"),
                func.count()
                .filter(Repair.status == RepairStatus.REPORTED)
                .label("reported"),
            )
        )

        return result.one()
