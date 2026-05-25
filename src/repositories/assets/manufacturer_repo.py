from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.manufacturer import Manufacturer
from repositories.base import BaseRepository


class ManufacturerRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        return await self.scalars(select(Manufacturer).order_by(Manufacturer.name))

    async def get(self, manufacturer_id):
        return await self.scalar(
            select(Manufacturer).where(Manufacturer.id == manufacturer_id)
        )

    async def get_by_slug(self, slug: str):
        return await self.scalar(select(Manufacturer).where(Manufacturer.slug == slug))

    async def get_by_normalized_name(self, normalized: str):
        return await self.scalars_first(
            select(Manufacturer).where(func.lower(Manufacturer.name) == normalized)
        )

    async def create(self, obj: Manufacturer):
        self.add(obj)
        await self.flush()
        await self.refresh(obj)
        return obj

    async def delete(self, obj: Manufacturer):
        await self.session.delete(obj)
