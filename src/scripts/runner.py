# src/scripts/runner.py

import asyncio
from typing import Callable, Awaitable
from core.database import get_session_factory


async def _run(func: Callable[[any], Awaitable[None]]):
    session_factory = get_session_factory()

    async with session_factory() as session:
        async with session.begin():
            await func(session)


def run(func):
    asyncio.run(_run(func))
