from uuid import UUID

from fastapi import APIRouter, Depends


from core.security.rbac.presets import IsSuperAdmin
from api.dependencies.rbac import get_rbac_service
from core.security.auth.types import CurrentUser
from services.rbac_service import RBACService
from schemas.rbac import (
    RoleOut,
    RoleCreate,
    RoleUpdate,
    RolePermissionsUpdate,
    PermissionOut,
)

router = APIRouter(prefix="/rbac", tags=["RBAC"])

# ROLES
@router.get("/roles", response_model=list[RoleOut])
async def list_roles(
    _: CurrentUser = Depends(IsSuperAdmin),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_roles()


@router.post("/roles", response_model=RoleOut)
async def create_role(
    data: RoleCreate,
    _: CurrentUser = Depends(IsSuperAdmin),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.create_role(data)


@router.patch("/roles/{role_id}", response_model=RoleOut)
async def update_role(
    role_id: UUID,
    data: RoleUpdate,
    _: CurrentUser = Depends(IsSuperAdmin),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.update_role(role_id, data.model_dump(exclude_unset=True))


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: UUID,
    _: CurrentUser = Depends(IsSuperAdmin),
    service: RBACService = Depends(get_rbac_service),
):
    await service.delete_role(role_id)
    return {"status": "deleted"}


# PERMISSIONS
@router.get("/permissions", response_model=list[PermissionOut])
async def list_permissions(
    _: CurrentUser = Depends(IsSuperAdmin),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_permissions()


# ROLE PERMISSIONS
@router.put("/roles/{role_id}/permissions", response_model=RoleOut)
async def set_role_permissions(
    role_id: UUID,
    data: RolePermissionsUpdate,
    _: CurrentUser = Depends(IsSuperAdmin),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.set_role_permissions(role_id, data.permission_ids)
