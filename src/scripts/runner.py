import asyncio
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_async import get_async_session_factory
from db.models import load_all_models


async def _run(func: Callable[[AsyncSession], Awaitable[None]]):
    load_all_models()
    session_factory = get_async_session_factory()

    async with session_factory() as session:
        async with session.begin():
            await func(session)


def run(func: Callable):
    asyncio.run(_run(func))
