# repositories/asset_model_repo.py

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset_model import AssetModel


class AssetModelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        result = await self.session.execute(
            select(AssetModel).order_by(AssetModel.name)
        )
        return result.scalars().all()

    async def get(self, model_id):
        result = await self.session.execute(
            select(AssetModel).where(AssetModel.id == model_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.session.execute(
            select(AssetModel).where(AssetModel.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_manufacturer(self, normalized: str, manufacturer_id):
        result = await self.session.execute(
            select(AssetModel).where(
                func.lower(AssetModel.name) == normalized,
                AssetModel.manufacturer_id == manufacturer_id,
            )
        )
        return result.scalars().first()

    async def create(self, obj: AssetModel):
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: AssetModel):
        await self.session.delete(obj)
