from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app import create_app
from core.config import get_settings
from core.security.passwords import hash_password
from db.dependencies import get_db_session
from db.meta import meta
from db.models import load_all_models
from db.models.enums import UserRole, UserStatus
from db.models.users.permission import Permission, Role
from db.models.users.user import User
from tests.utils.auth import login

pytest_plugins = ("tests.fixtures.analytics",)


# ---------------- ENGINE ----------------


@pytest.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    settings = get_settings()

    load_all_models()

    engine = create_async_engine(str(settings.postgres_async_url), echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


# ---------------- SESSION ----------------


@pytest.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:

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


# ---------------- APP ----------------


@pytest.fixture
async def fastapi_app(dbsession: AsyncSession) -> FastAPI:
    app = create_app()

    async def override_db():
        yield dbsession

    app.dependency_overrides[get_db_session] = override_db

    # отключаем audit middleware в тестах
    app.user_middleware = [
        m for m in app.user_middleware if m.cls.__name__ != "AuditMiddleware"
    ]

    return app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:

    transport = ASGITransport(
        app=fastapi_app,
        raise_app_exceptions=True,
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client


# ---------------- USER FACTORY ----------------


@pytest.fixture
async def create_user(dbsession):
    async def _create(login="test_user", password="password"):
        role_result = await dbsession.execute(
            select(Role).where(Role.code == UserRole.SUPERADMIN.value)
        )
        role = role_result.scalar_one_or_none()

        if not role:
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
            email=f"{login}_{suffix}@test.com",
            phone=f"+998900{suffix[:6]}",
            role_id=role.id,
            status=UserStatus.ACTIVE.value,
        )

        dbsession.add(user)
        await dbsession.commit()

        return user

    return _create


# ---------------- SUPERADMIN ----------------


@pytest.fixture
async def superadmin(create_user):
    return await create_user(login="superadmin", password="password")


@pytest.fixture
async def superadmin_token(client: AsyncClient, superadmin):
    _, access_token = await login(client, "superadmin", "password")
    return access_token


# ---------------- PERMISSIONS ----------------


@pytest.fixture
async def permission_id(dbsession):
    perm = Permission(name="Test", code="test_perm")
    dbsession.add(perm)
    await dbsession.commit()
    return perm.id


# ---------------- ROLE ----------------


@pytest.fixture
async def role_id(client, superadmin_token):
    res = await client.post(
        "/rbac/roles",
        json={"name": "TestRole", "code": "testrole"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    return res.json()["id"]


@pytest.fixture
async def role_with_users(dbsession):
    role = Role(name="RoleWithUsers", code="role_with_users")
    dbsession.add(role)
    await dbsession.flush()

    user = User(
        login="user2",
        password_hash=hash_password("password"),
        email="user2@test.com",
        phone="+998900000000",
        role_id=role.id,
        status=UserStatus.ACTIVE.value,
    )
    dbsession.add(user)

    await dbsession.commit()

    return role.id
