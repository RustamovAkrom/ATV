from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy import select

from db.models.users.user import User
from db.models.users.permission import Role
from db.models.enums import UserRole, UserStatus
from core.security.passwords import hash_password
from app import create_app
from core.config import get_settings
from db.dependencies import get_db_session
from db.meta import meta
from db.models import load_all_models


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    settings = get_settings()

    load_all_models()

    engine = create_async_engine(str(settings.postgres_async_url), echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest.fixture
async def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    app = create_app()

    async def override_db():
        yield dbsession

    app.dependency_overrides[get_db_session] = override_db

    app.user_middleware = [
        m for m in app.user_middleware
        if m.cls.__name__ != "AuditMiddleware"
    ]
    return app  # noqa: WPS331


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    transport = ASGITransport(
        app=fastapi_app,
        raise_app_exceptions=True,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client



@pytest.fixture
async def create_user(dbsession):
    async def _create(
        login: str = "test_user",
        password: str = "password",
        email: str | None = None,
        phone: str | None = None,
    ):
        role_result = await dbsession.execute(
            select(Role).where(Role.code == UserRole.SUPERADMIN.value)
        )
        role = role_result.scalar_one_or_none()

        if role is None:
            role = Role(
                name="SuperAdmin",
                code=UserRole.SUPERADMIN.value,
            )
            dbsession.add(role)
            await dbsession.flush()

        suffix = uuid4().hex[:8]

        user = User(
            login=login,
            password_hash=hash_password(password),
            email=email or f"{login}_{suffix}@test.com",
            phone=phone or f"+998900{suffix[:6]}",
            role_id=role.id,
            status=UserStatus.ACTIVE.value,
        )

        dbsession.add(user)
        await dbsession.flush()
        return user

    return _create
