from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.rbac import get_rbac_service
from core.cache.decorators import cached, invalidate_cache
from core.security.rbac.presets import RBACPermissions, UserPermissions
from core.slowapi import limiter
from schemas.auth import CurrentUserSchema
from schemas.common import StatusResponse
from schemas.rbac.rbac import (
    PermissionOutSchema,
    RoleCreateSchema,
    RoleOutSchema,
    RolePermissionsUpdateSchema,
    RoleUpdateSchema,
)
from services.rbac.rbac_service import RBACService

router = APIRouter(prefix="/rbac", tags=["RBAC"])


@router.get("/roles", response_model=list[RoleOutSchema])
@cached(tags=("roles:list",))
async def list_roles(
    _: CurrentUserSchema = Depends(UserPermissions.CanViewUsers),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_roles()


@router.get("/permissions", response_model=list[PermissionOutSchema])
@cached(tags=("permissions:list",))
async def list_permissions(
    # Список прав полезен админу при настройке системы
    _: CurrentUserSchema = Depends(UserPermissions.CanViewUsers),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.list_permissions()


@router.post("/roles", response_model=RoleOutSchema)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "roles:list",
        "permissions:list",
    )
)
async def create_role(
    request: Request,
    data: RoleCreateSchema,
    _: CurrentUserSchema = Depends(RBACPermissions.CanManageRoles),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.create_role(data)


@router.patch("/roles/{role_id}", response_model=RoleOutSchema)
@limiter.limit("20/minute")
@invalidate_cache(
    tags=(
        "roles:list",
        "permissions:list",
    )
)
async def update_role(
    request: Request,
    role_id: UUID,
    data: RoleUpdateSchema,
    _: CurrentUserSchema = Depends(RBACPermissions.CanManageRoles),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.update_role(role_id, data)


@router.delete("/roles/{role_id}", response_model=StatusResponse)
@limiter.limit("5/minute")
@invalidate_cache(
    tags=(
        "roles:list",
        "permissions:list",
    )
)
async def delete_role(
    request: Request,
    role_id: UUID,
    _: CurrentUserSchema = Depends(RBACPermissions.CanManageRoles),
    service: RBACService = Depends(get_rbac_service),
):
    await service.delete_role(role_id)
    return StatusResponse(status="deleted", message="Role deleted successfully")


@router.put("/roles/{role_id}/permissions", response_model=RoleOutSchema)
@limiter.limit("10/minute")
@invalidate_cache(
    tags=(
        "roles:list",
        "permissions:list",
    )
)
async def set_role_permissions(
    request: Request,
    role_id: UUID,
    data: RolePermissionsUpdateSchema,
    _: CurrentUserSchema = Depends(RBACPermissions.CanManageRoles),
    service: RBACService = Depends(get_rbac_service),
):
    return await service.set_role_permissions(role_id, data.permission_ids)
