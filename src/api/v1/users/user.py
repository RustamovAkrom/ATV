from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.users import get_user_service
from core.cache.decorators import cached, invalidate_cache
from core.exceptions.errors import BadRequest
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from db.models.users.user import User
from schemas.auth import CurrentUserSchema
from schemas.pagination import PaginationParamsSchema
from schemas.users import (
    AdminUserUpdateSchema,
    ChangePasswordRequestSchema,
    UserCreateSchema,
    UserOutSchema,
    UserUpdateSchema,
)
from services.users.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _to_user_out(user: User) -> UserOutSchema:
    role = getattr(user.role, "code", None)
    permissions = [
        str(getattr(permission, "code", getattr(permission, "value", permission)))
        for permission in (getattr(user, "permissions", None) or [])
    ]

    return UserOutSchema(
        id=user.id,
        login=user.login,
        email=user.email,
        phone=user.phone,
        role=str(role).lower() if role else None,
        permissions=permissions,
        first_name=getattr(user, "first_name", None),
        last_name=getattr(user, "last_name", None),
        status=getattr(user, "status", None),
        created_at=getattr(user, "created_at", None),
        updated_at=getattr(user, "updated_at", None),
    )


@router.get("/me", response_model=UserOutSchema)
@cached(ttl=60, tags=("users:me",))
async def me(
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get(current_user.id)
    return _to_user_out(user)


@router.patch("/me", response_model=UserOutSchema)
@invalidate_cache(tags=("users:list", "users:search", "users:detail", "users:me"))
async def update_me(
    data: UserUpdateSchema,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.update(current_user.id, data)
    return _to_user_out(user)


@router.post("/me/change-password")
@invalidate_cache(tags=("users:me",))
async def change_password(
    data: ChangePasswordRequestSchema,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.change_password(
        current_user.id,
        data.old_password,
        data.new_password,
    )
    return {"status": "ok"}


@router.get(
    "/", response_model=list[UserOutSchema], dependencies=[presets.CanViewUsers]
)
@cached(ttl=60, tags=("users:list",))
async def list_users(
    service: UserService = Depends(get_user_service),
    pagination: PaginationParamsSchema = Depends(),
):
    users = await service.get_all(pagination)
    return [_to_user_out(user) for user in users]


@router.post("/", response_model=UserOutSchema, dependencies=[presets.CanCreateUsers])
@invalidate_cache(tags=("users:list", "users:search"))
async def create_user(
    data: UserCreateSchema,
    service: UserService = Depends(get_user_service),
):
    user = await service.create(data)
    user = await service.get(user.id)
    return _to_user_out(user)


@router.get(
    "/search", response_model=list[UserOutSchema], dependencies=[presets.CanViewUsers]
)
@cached(ttl=30, tags=("users:search",))
async def search_users(
    q: str,
    service: UserService = Depends(get_user_service),
    pagination: PaginationParamsSchema = Depends(),
):
    users = await service.search(q, pagination)
    return [_to_user_out(user) for user in users]


@router.get(
    "/{user_id}", response_model=UserOutSchema, dependencies=[presets.CanViewUsers]
)
@cached(ttl=60, tags=("users:detail",))
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
):
    user = await service.get(user_id)
    return _to_user_out(user)


@router.patch("/{user_id}", response_model=UserOutSchema)
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def update_user(
    user_id: UUID,
    data: AdminUserUpdateSchema,
    current_user: CurrentUserSchema = presets.CanManageUsers,
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot modify yourself. Use /me")

    user = await service.admin_update(user_id, data)
    return _to_user_out(user)


@router.delete("/{user_id}")
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def archive_user(
    user_id: UUID,
    current_user: CurrentUserSchema = presets.CanDeleteUsers,
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot delete yourself")

    await service.archive(user_id)
    return {"status": "archived"}


@router.post("/{user_id}/block")
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def block_user(
    user_id: UUID,
    current_user: CurrentUserSchema = presets.CanManageUsers,
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot block yourself")

    await service.block(user_id)
    return {"status": "blocked"}


@router.post("/{user_id}/activate")
@invalidate_cache(tags=("users:list", "users:search", "users:detail"))
async def activate_user(
    user_id: UUID,
    current_user: CurrentUserSchema = presets.CanManageUsers,
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise BadRequest("Cannot activate yourself")

    await service.activate(user_id)
    return {"status": "active"}
