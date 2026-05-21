from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset_class import AssetClass
from repositories.base import BaseRepository


class AssetClassRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        return await self.scalars(
            select(AssetClass).order_by(AssetClass.name)
        )

    async def get(self, class_id: UUID):
        return await self.scalar(
            select(AssetClass).where(AssetClass.id == class_id)
        )

    async def get_by_slug(self, slug: str):
        return await self.scalar(
            select(AssetClass).where(AssetClass.slug == slug)
        )

    async def get_by_normalized_name(self, normalized: str):
        return await self.scalars_first(
            select(AssetClass).where(func.lower(AssetClass.name) == normalized)
        )

    async def create(self, obj: AssetClass):
        self.add(obj)
        await self.flush()
        await self.refresh(obj)
        return obj

    async def delete(self, obj: AssetClass):
        await self.session.delete(obj)
