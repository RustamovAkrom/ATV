from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_async import get_async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_async_session_factory()

    async with session_factory() as session:
        async with session.begin():
            yield session
# from collections.abc import AsyncGenerator

# from sqlalchemy.ext.asyncio import AsyncSession

# from core.database import get_session_factory


# async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
#     """
#     Create and get database session.

#     :param request: current request.
#     :yield: database session.
#     """
#     session_factory = get_session_factory()
#     session = session_factory()

#     try:
#         yield session
#         await session.commit()
#     except Exception:
#         await session.rollback()
#         raise
#     finally:
#         await session.close()
