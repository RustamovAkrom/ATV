from sqlalchemy import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.errors import Conflict


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, obj):
        self.session.add(obj)
        return obj

    async def delete(self, obj):
        await self.session.delete(obj)

    # DB Operations (Async)
    async def flush(self) -> None:
        try:
            await self.session.flush()
        except IntegrityError as e:
            raise Conflict("Database constraint violated") from e

    async def refresh(self, obj):
        await self.session.refresh(obj)

    async def execute(self, stmt) -> Result:
        return await self.session.execute(stmt)

    @staticmethod
    def _rowcount(result: Result) -> int:
        return int(getattr(result, "rowcount", 0) or 0)

    async def scalar(self, stmt):
        result = await self.execute(stmt)
        return result.scalar_one_or_none()

    async def scalar_one(self, stmt):
        result = await self.execute(stmt)
        return result.scalar_one()

    async def scalars(self, stmt):
        result = await self.execute(stmt)
        return list(result.scalars().all())

    async def scalars_first(self, stmt):
        result = await self.execute(stmt)
        return result.scalars().first()

    async def scalars_unique_all(self, stmt):
        result = await self.execute(stmt)
        return result.scalars().unique().all()

    async def get_or_404(self, stmt, message="Not Found"):
        obj = await self.scalar(stmt)
        if not obj:
            from core.exceptions.errors import NotFound

            raise NotFound(message)
        return obj
