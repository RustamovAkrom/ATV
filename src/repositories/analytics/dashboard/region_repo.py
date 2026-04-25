from sqlalchemy import func, select

from db.models.assets.asset import Asset
from db.models.enums import AssetStatus
from db.models.org.region import Region


class RegionAnalyticsRepository:
    def __init__(self, session):
        self.session = session

    async def get_region_stats(self):
        result = await self.session.execute(
            select(
                Region.id,
                Region.name,
                Region.latitude,
                Region.longitude,
                Region.geojson,
                func.count(Asset.id).label("total"),
                func.count().filter(Asset.status == AssetStatus.ACTIVE).label("active"),
                func.count()
                .filter(Asset.status == AssetStatus.ASSIGNED)
                .label("assigned"),
                func.count()
                .filter(Asset.status == AssetStatus.ARCHIVED)
                .label("archived"),
                func.count()
                .filter(Asset.status == AssetStatus.IN_REPAIR)
                .label("repair"),
            )
            .outerjoin(Asset, Asset.region_id == Region.id)
            .group_by(
                Region.id,
                Region.name,
                Region.latitude,
                Region.longitude,
                Region.geojson,
            )
        )

        return result.all()
