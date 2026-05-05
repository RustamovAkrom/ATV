# repositories/asset_model_repo.py

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from core.exceptions.errors import Conflict

from db.models.assets.asset_model import AssetModel
from repositories.base import BaseRepository


class AssetModelRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        return await self.scalars(
            select(AssetModel).order_by(AssetModel.name)
        )

    async def get(self, model_id):
        return await self.scalar(
            select(AssetModel).where(AssetModel.id == model_id)
        )

    async def get_by_code(self, code: str):
        return await self.scalar(
            select(AssetModel).where(AssetModel.code == code)
        )

    async def get_by_name_and_manufacturer(self, normalized: str, manufacturer_id):
        return await self.scalars_first(
            select(AssetModel).where(
                func.lower(AssetModel.name) == normalized,
                AssetModel.manufacturer_id == manufacturer_id,
            )
        )

    async def create(self, obj: AssetModel):
        self.add(obj)
        await self.flush()
        await self.refresh(obj)
        return obj

    # Ovverrided
    async def delete(self, obj: AssetModel):
        await self.session.delete(obj)
