from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from core.exceptions.errors import Conflict
from db.models.assets.asset_category import AssetCategory
from repositories.base import BaseRepository


class AssetCategoryRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        return await self.scalars(
            select(AssetCategory).order_by(AssetCategory.name)
        )

    async def get(self, category_id: UUID):
        return await self.scalar(
            select(AssetCategory).where(AssetCategory.id == category_id)
        )

    async def get_by_slug(self, slug: str):
        return await self.scalar(
            select(AssetCategory).where(AssetCategory.slug == slug)
        )

    async def get_by_normalized_name(self, name: str):
        return await self.scalar(
            select(AssetCategory).where(func.lower(AssetCategory.name) == name)
        )

    async def exists_by_slug(self, slug: str) -> bool:
        return await self.scalar(
            select(AssetCategory.id).where(AssetCategory.slug == slug)
        ) is not None

    async def create(self, obj: AssetCategory):
        self.add(obj)
        await self.flush()
        await self.refresh(obj)
        return obj

    # Overrided
    async def delete(self, obj: AssetCategory):
        await self.session.delete(obj)
