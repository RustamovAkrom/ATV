from uuid import UUID
from fastapi import APIRouter, Depends

from api.dependencies.rbac import get_rbac_service
from core.security.auth.types import CurrentUser
# Используем наши пресеты для гибкого управления
from core.security.rbac import presets
from schemas.rbac import (
    PermissionOut,
    RoleCreate,
    RoleOut,
    RolePermissionsUpdate,
    RoleUpdate,
)
from services.rbac_service import RBACService

router = APIRouter(prefix="/rbac", tags=["RBAC"])

# --- ЧТЕНИЕ (Доступно тем, кто управляет пользователями или аудитом) ---

@router.get("/roles", response_model=list[RoleOut])
async def list_roles(
    # Позволяем просмотр тем, у кого есть права на просмотр ролей (Админы/Суперы)
    _: CurrentUser = presets.CanViewUsers,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_roles()


@router.get("/permissions", response_model=list[PermissionOut])
async def list_permissions(
    # Список прав полезен админу при настройке системы
    _: CurrentUser = presets.CanViewUsers,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_permissions()


# --- УПРАВЛЕНИЕ (Критически важные операции - только SuperAdmin / ManageRoles) ---

@router.post("/roles", response_model=RoleOut)
async def create_role(
    data: RoleCreate,
    # Здесь нужна максимальная привилегия
    _: CurrentUser = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.create_role(data)


@router.patch("/roles/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    _: CurrentUser = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.update_role(role_id, data)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    _: CurrentUser = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    await service.delete_role(role_id)
    return {"status": "deleted"}


@router.put("/roles/{role_id}/permissions", response_model=RoleOut)
async def set_role_permissions(
    role_id: UUID,
    data: RolePermissionsUpdate,
    # Изменение матрицы прав — самая опасная операция
    _: CurrentUser = presets.CanManageRoles,
    service: RBACService = Depends(get_rbac_service),
):
    return await service.set_role_permissions(role_id, data.permission_ids)
