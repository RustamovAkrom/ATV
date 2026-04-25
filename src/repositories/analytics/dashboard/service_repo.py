from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset import Asset
from db.models.enums import AssetStatus
from db.models.org.service import Service


class ServiceAnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_service_stats(self):
        result = await self.session.execute(
            select(
                Service.id,
                Service.name,
                func.count(Asset.id).label("total"),
                func.count().filter(Asset.status == AssetStatus.ACTIVE).label("active"),
                func.count()
                .filter(Asset.status == AssetStatus.IN_REPAIR)
                .label("repair"),
            )
            .outerjoin(Asset, Asset.service_id == Service.id)
            .group_by(Service.id)
        )
        return result.all()
