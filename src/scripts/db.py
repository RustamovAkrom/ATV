import asyncio
from core.database import get_session_factory

async def run_db(func):
    session_factory = get_session_factory()
    async with session_factory() as session:
        async with session.begin():
            await func(session)


def run(func):
    asyncio.run(run_db(func))
