from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.assets.manufacturer import Manufacturer


class ManufacturerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self):
        result = await self.session.execute(
            select(Manufacturer).order_by(Manufacturer.name)
        )
        return result.scalars().all()

    async def get(self, manufacturer_id):
        result = await self.session.execute(
            select(Manufacturer).where(Manufacturer.id == manufacturer_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str):
        result = await self.session.execute(
            select(Manufacturer).where(Manufacturer.code == code)
        )
        return result.scalar_one_or_none()

    async def get_by_normalized_name(self, normalized: str):
        result = await self.session.execute(
            select(Manufacturer).where(
                func.lower(Manufacturer.name) == normalized
            )
        )
        return result.scalars().first()

    async def create(self, obj: Manufacturer):
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete(self, obj: Manufacturer):
        await self.session.delete(obj)
