from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_async import get_async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_async_session_factory()

    async with session_factory() as session:
        async with session.begin():
            yield session
