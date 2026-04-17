from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser
from core.security.rbac.presets import IsAdmin
from services.user_service import UserService
from api.dependencies.users import get_user_service
from schemas.users import (
    UserCreate,
    UserUpdate,
    AdminUserUpdate,
    UserOut,
    ChangePasswordRequest,
)
from db.models.users.user import User
from schemas.pagination import PaginationParams


router = APIRouter(prefix="/users", tags=["Users"])


def _to_user_out(user: User) -> UserOut:
    role = getattr(user.role, "code", None)
    permissions = [
        str(getattr(permission, "code", getattr(permission, "value", permission)))
        for permission in (getattr(user, "permissions", None) or [])
    ]

    return UserOut(
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


@router.get("/me", response_model=UserOut)
async def me(
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get(current_user.id)
    return _to_user_out(user)


@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.update(current_user.id, data)
    return _to_user_out(user)


@router.post("/me/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    await service.change_password(
        current_user.id,
        data.old_password,
        data.new_password,
    )
    return {"status": "ok"}

# ADMIN
@router.get("/", response_model=list[UserOut])
async def list_users(
    _: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
    pagination: PaginationParams = Depends(),
):
    users = await service.get_all(pagination.limit, pagination.offset())
    return [_to_user_out(user) for user in users]


@router.post("/", response_model=UserOut)
async def create_user(
    data: UserCreate,
    _: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    user = await service.create(data)
    user = await service.get(user.id)
    return _to_user_out(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    current_user: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot modify yourself")

    user = await service.admin_update(user_id, data)
    return _to_user_out(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    _: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    user = await service.get(user_id)
    return _to_user_out(user)


@router.delete("/{user_id}")
async def archive_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot delete yourself")

    await service.archive(user_id)
    return {"status": "archived"}


@router.post("/{user_id}/block")
async def block_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot block yourself")

    await service.block(user_id)
    return {"status": "blocked"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    _: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    await service.activate(user_id)
    return {"status": "active"}
