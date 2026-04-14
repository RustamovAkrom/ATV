"""
Dependency Injection Layer (API)

This package contains FastAPI dependency providers used to construct
application services and repositories.

Purpose:
---------
Centralize all dependency wiring (Depends) in one place and keep
business logic layers (services, repositories) framework-agnostic.

Architecture:
-------------
API → dependencies → services → repositories → database

Rules:
------
1. Only this layer may use `Depends`.
2. Services and Repositories MUST NOT depend on FastAPI.
3. Do not import dependencies between modules (avoid circular imports).
4. Each module represents a domain (auth, users, sessions, etc.).

Usage:
------
In API routes:

    from api.dependencies.users import get_user_service

    @router.get("/users")
    async def list_users(service = Depends(get_user_service)):
        return await service.get_all()

Notes:
------
- Dependencies are lightweight factories.
- They should only construct and return objects.
- No business logic should live here.

"""
