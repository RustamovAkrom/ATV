# api/v1/assets/asset_assignments.py (новый файл)
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_assignment import get_asset_assignment_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.slowapi import limiter
from schemas.assets.asset_assignments import (
    AssetAssignmentActionSchema,
    AssetAssignmentRequest,
    AssetReassignmentRequest,
)
from schemas.auth import CurrentUserSchema
from services.assets.asset_assignment_service import AssetAssignmentService

router = APIRouter(prefix="/assets/{asset_id}/assignments", tags=["Asset Assignments"])


@router.post("/self", response_model=AssetAssignmentActionSchema)
@limiter.limit("20/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def assign_asset_to_self(
    request: Request,
    asset_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
):
    """
    Назначить актив СЕБЕ (доступно всем пользователям)
    """
    return await service.assign_asset(asset_id, actor.id, actor)


@router.post("/", response_model=AssetAssignmentActionSchema)
@limiter.limit("20/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def assign_asset_to_user(
    request: Request,
    asset_id: UUID,
    data: AssetAssignmentRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
):
    """
    Назначить актив ДРУГОМУ пользователю.

    Требует права ASSETS_ASSIGN (только ADMIN и выше)
    """
    from core.security.rbac.guards import check_permissions
    from core.security.rbac.permissions import Permissions

    # Проверка права назначать других
    check_permissions(actor, Permissions.ASSETS_ASSIGN)

    return await service.assign_asset(asset_id, data.user_id, actor)


@router.delete("/", response_model=AssetAssignmentActionSchema)
@limiter.limit("20/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def unassign_asset(
    request: Request,
    asset_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
):
    """
    Снять назначение с актива.

    - Владелец актива может снять назначение с себя (без доп. прав)
    - Для снятия с другого пользователя нужно право ASSETS_UNASSIGN
    """
    from core.security.rbac.guards import check_permissions
    from core.security.rbac.permissions import Permissions

    # Получаем актив чтобы проверить владельца
    asset = await service.repo.get_asset_for_update(asset_id)

    # Если снимаем не с себя - нужны права
    if asset.owner_id != actor.id:
        check_permissions(actor, Permissions.ASSETS_UNASSIGN)

    return await service.unassign_asset(asset_id, actor)


@router.put("/reassign", response_model=AssetAssignmentActionSchema)
@limiter.limit("20/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def reassign_asset(
    request: Request,
    asset_id: UUID,
    data: AssetReassignmentRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
):
    """
    Переназначить актив от текущего владельца другому пользователю.

    Требует права ASSETS_ASSIGN (только ADMIN и выше)
    """
    from core.security.rbac.guards import check_permissions
    from core.security.rbac.permissions import Permissions

    check_permissions(actor, Permissions.ASSETS_ASSIGN)

    return await service.reassign_asset(asset_id, data.new_user_id, actor)


@router.get("/active", response_model=AssetAssignmentActionSchema | None)
@limiter.limit("30/minute")
async def get_active_assignment(
    request: Request,
    asset_id: UUID,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: AssetAssignmentService = Depends(get_asset_assignment_service),
):
    """
    Получить активное назначение актива.

    Доступно всем авторизованным пользователям.
    """
    return await service.get_active_assignment(asset_id)
