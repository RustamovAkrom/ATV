from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset import Asset
from db.models.assets.asset_model import AssetModel


class TopAssetsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_top_assets(self, limit: int = 5):
        result = await self.session.execute(
            select(
                AssetModel.name,
                func.count(Asset.id).label("count"),
            )
            .join(Asset, Asset.model_id == AssetModel.id)
            .group_by(AssetModel.name)
            .order_by(func.count(Asset.id).desc())
            .limit(limit)
        )

        return result.all()
