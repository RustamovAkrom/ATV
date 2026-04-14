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

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
async def me(current_user: CurrentUser = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.update(current_user.id, data)


@router.post("/me/change-password")
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_current_user),
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
    limit: int = Query(20, le=100),
    page: int = Query(0),
):
    return await service.get_all(limit, page * limit)


@router.post("/", response_model=UserOut)
async def create_user(
    data: UserCreate,
    _: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    return await service.create(data)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    current_user: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot modify yourself")

    return await service.admin_update(user_id, data)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    _: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    return await service.get(user_id)


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


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: CurrentUser = Depends(IsAdmin),
    service: UserService = Depends(get_user_service),
):
    if user_id == current_user.id:
        raise HTTPException(400, "Cannot delete yourself")

    await service.delete(user_id)
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
