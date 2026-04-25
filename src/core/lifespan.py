from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database.db_async import get_async_session_factory, get_db_async_engine
from core.requests import get_http_transport
from scripts.bootstrap.rbac import seed_rbac


async def run_bootstrap():
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        async with session.begin():
            await seed_rbac(session)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    db_engine = get_db_async_engine()
    http_transport = get_http_transport()
    yield
    await db_engine.dispose()
    await http_transport.aclose()
