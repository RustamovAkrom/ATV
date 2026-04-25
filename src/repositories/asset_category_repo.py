from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.assets.asset_category import AssetCategory


class AssetCategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        result = await self.session.execute(
            select(AssetCategory).order_by(AssetCategory.name)
        )
        return result.scalars().all()

    async def get(self, category_id: UUID):
        result = await self.session.execute(
            select(AssetCategory).where(AssetCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.session.execute(
            select(AssetCategory).where(AssetCategory.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_normalized_name(self, name: str):
        result = await self.session.execute(
            select(AssetCategory).where(
                func.lower(AssetCategory.name) == name
            )
        )
        return result.scalar_one_or_none()

    async def exists_by_code(self, code: str) -> bool:
        result = await self.session.execute(
            select(AssetCategory.id).where(AssetCategory.code == code)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, obj: AssetCategory):
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: AssetCategory):
        await self.session.delete(obj)
