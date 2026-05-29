from uuid import UUID

from fastapi import APIRouter, Depends, Request

from api.dependencies.assets.asset_approval import get_approval_service
from core.cache.decorators import invalidate_cache
from core.security.auth.dependencies import get_current_user
from core.security.rbac.presets import AssetApprovalPermissions
from core.slowapi import limiter
from schemas.assets.approvals import ApprovalCreate, ApprovalSchema
from schemas.assets.asset_assignments import AssetAssignmentRequest
from schemas.assets.asset_transfers import AssetTransferCreate
from schemas.assets.repairs import RepairCompleteRequest
from schemas.assets.warehouses import WarehouseMoveRequest
from schemas.auth import CurrentUserSchema
from services.approvals.approval_service import ApprovalService

router = APIRouter(
    prefix="/assets/{asset_id}/approval-requests",
    tags=["Asset Approval Requests"],
)


@router.post(
    "/assignment",
    response_model=ApprovalSchema,
    dependencies=[Depends(AssetApprovalPermissions.CanCreateApprovals)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def request_assignment(
    request: Request,
    asset_id: UUID,
    data: AssetAssignmentRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.create(
        ApprovalCreate(
            entity_type="asset_assignment",
            entity_id=asset_id,
            action="assign",
            payload={"user_id": str(data.user_id)},
        ),
        actor,
    )


@router.post(
    "/transfer",
    response_model=ApprovalSchema,
    dependencies=[Depends(AssetApprovalPermissions.CanCreateApprovals)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def request_transfer(
    request: Request,
    asset_id: UUID,
    data: AssetTransferCreate,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.create(
        ApprovalCreate(
            entity_type="asset_transfer",
            entity_id=asset_id,
            action="create_transfer",
            payload=data.model_dump(exclude_none=True),
        ),
        actor,
    )


@router.post(
    "/repair/{repair_id}/complete",
    response_model=ApprovalSchema,
    dependencies=[Depends(AssetApprovalPermissions.CanCreateApprovals)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history", "repair:detail"))
async def request_repair_complete(
    request: Request,
    asset_id: UUID,
    repair_id: UUID,
    data: RepairCompleteRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    payload = data.model_dump(exclude_none=True)
    payload["repair_id"] = str(repair_id)

    return await service.create(
        ApprovalCreate(
            entity_type="repair",
            entity_id=asset_id,
            action="complete_repair",
            payload=payload,
        ),
        actor,
    )


@router.post(
    "/warehouse-move",
    response_model=ApprovalSchema,
    dependencies=[Depends(AssetApprovalPermissions.CanCreateApprovals)],
)
@limiter.limit("10/minute")
@invalidate_cache(tags=("asset:list", "asset:detail", "asset:history"))
async def request_warehouse_move(
    request: Request,
    asset_id: UUID,
    data: WarehouseMoveRequest,
    actor: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.create(
        ApprovalCreate(
            entity_type="asset",
            entity_id=asset_id,
            action="move_to_warehouse",
            payload=data.model_dump(exclude_none=True),
        ),
        actor,
    )
