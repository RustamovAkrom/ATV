from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.rbac import get_rbac_service

# Используем наши пресеты для гибкого управления
from core.security.rbac import presets
from schemas.auth import CurrentUserSchema
from schemas.rbac.rbac import (
    PermissionOutSchema,
    RoleCreateSchema,
    RoleOutSchema,
    RolePermissionsUpdateSchema,
    RoleUpdateSchema,
)
from services.rbac.rbac_service import RBACService

router = APIRouter(prefix="/rbac", tags=["RBAC"])

# --- ЧТЕНИЕ (Доступно тем, кто управляет пользователями или аудитом) ---


@router.get("/roles", response_model=list[RoleOutSchema])
async def list_roles(
    # Позволяем просмотр тем, у кого есть права на просмотр ролей (Админы/Суперы)
    current_user: CurrentUserSchema = presets.CanViewUsers,
    service: RBACService = Depends(get_rbac_service),
):
    print(current_user)
    return await service.list_roles()


@router.get("/permissions", response_model=list[PermissionOutSchema])
async def list_permissions(
    # Список прав полезен админу при настройке системы
    _: CurrentUserSchema = presets.CanViewUsers,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_permissions()


# --- УПРАВЛЕНИЕ (Критически важные операции - только SuperAdmin / ManageRoles) ---


@router.post("/roles", response_model=RoleOutSchema)
async def create_role(
    data: RoleCreateSchema,
    # Здесь нужна максимальная привилегия
    _: CurrentUserSchema = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.create_role(data)


@router.patch("/roles/{role_id}", response_model=RoleOutSchema)
async def update_role(
    role_id: UUID,
    data: RoleUpdateSchema,
    _: CurrentUserSchema = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.update_role(role_id, data)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    _: CurrentUserSchema = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    await service.delete_role(role_id)
    return {"status": "deleted"}


@router.put("/roles/{role_id}/permissions", response_model=RoleOutSchema)
async def set_role_permissions(
    role_id: UUID,
    data: RolePermissionsUpdateSchema,
    # Изменение матрицы прав — самая опасная операция
    _: CurrentUserSchema = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.set_role_permissions(role_id, data.permission_ids)
