import asyncio
from typing import Callable, Awaitable

from core.database.db_async import get_async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


async def _run(func: Callable[[AsyncSession], Awaitable[None]]):
    session_factory = get_async_session_factory()

    async with session_factory() as session:
        async with session.begin():
            await func(session)


def run(func: Callable):
    asyncio.run(_run(func))
