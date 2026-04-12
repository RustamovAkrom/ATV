from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import get_db_engine
from core.requests import get_http_transport

from scripts.bootstrap.roles import seed_roles_permissions
from core.database import get_session_factory


async def run_bootstrap():
    session_factory = get_session_factory()
    async with session_factory() as session:
        async with session.begin():
            await seed_roles_permissions(session)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_engine = get_db_engine()
    http_transport = get_http_transport()
    await run_bootstrap()
    yield
    await db_engine.dispose()
    await http_transport.aclose()
