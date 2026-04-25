from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models.assets.asset_class import AssetClass


class AssetClassRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        result = await self.session.execute(
            select(AssetClass).order_by(AssetClass.name)
        )
        return result.scalars().all()

    async def get(self, class_id: UUID):
        result = await self.session.execute(
            select(AssetClass).where(AssetClass.id == class_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.session.execute(
            select(AssetClass).where(AssetClass.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_normalized_name(self, normalized: str):
        result = await self.session.execute(
            select(AssetClass).where(
                func.lower(AssetClass.name) == normalized
            )
        )
        return result.scalars().first()

    async def create(self, obj: AssetClass):
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: AssetClass):
        await self.session.delete(obj)
