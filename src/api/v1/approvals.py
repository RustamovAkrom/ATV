from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.assets import get_approval_service
from core.security.auth.dependencies import get_current_user
from core.security.auth.types import CurrentUser
from core.security.rbac import presets
from schemas.approvals import ApprovalCreate, ApprovalDecision, ApprovalSchema
from services.approval_service import ApprovalService

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("/", response_model=list[ApprovalSchema], dependencies=[presets.IsAdmin])
async def list_approvals(
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.list()


@router.post("/", response_model=ApprovalSchema, dependencies=[presets.CanUpdateAssets])
async def create_approval(
    data: ApprovalCreate,
    current_user: CurrentUser = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.create(data, current_user.id)


@router.post("/{approval_id}/approve", response_model=ApprovalSchema, dependencies=[presets.IsAdmin])
async def approve_approval(
    approval_id: UUID,
    data: ApprovalDecision,
    current_user: CurrentUser = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.approve(approval_id, current_user.id, data.comment)


@router.post("/{approval_id}/reject", response_model=ApprovalSchema, dependencies=[presets.IsAdmin])
async def reject_approval(
    approval_id: UUID,
    data: ApprovalDecision,
    current_user: CurrentUser = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    return await service.reject(approval_id, current_user.id, data.comment)
