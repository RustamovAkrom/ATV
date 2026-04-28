from uuid import UUID

from fastapi import APIRouter, Depends, Query
from db.models.enums import ApprovalStatus

from api.dependencies.assets import get_approval_service
from core.security.auth.dependencies import get_current_user
from core.security.rbac import presets
from schemas.assets.approvals import ApprovalCreate, ApprovalDecision, ApprovalSchema
from schemas.auth import CurrentUserSchema
from services.approvals.approval_service import ApprovalService
from schemas.pagination import PaginationParamsSchema
from schemas.pagination import PageOutSchema
from api.dependencies.paginations import get_pagination


router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get(
    "/",
    response_model=PageOutSchema[ApprovalSchema],
    dependencies=[presets.CanViewApprovals],
)
async def list_approvals(
    status: ApprovalStatus | None = Query(None),
    pagination: PaginationParamsSchema = Depends(get_pagination),
    service: ApprovalService = Depends(get_approval_service),
):
    """
    List all approval requests (pending, approved, rejected).
    Requires: approvals.view permission
    """
    return await service.list(status, pagination)


@router.post(
    "/", response_model=ApprovalSchema, dependencies=[presets.CanCreateApprovals]
)
async def create_approval(
    data: ApprovalCreate,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    """
    Create a new approval request.
    Requires: approvals.create permission
    """
    return await service.create(data, current_user)


@router.post(
    "/{approval_id}/approve",
    response_model=ApprovalSchema,
    dependencies=[presets.CanApproveApprovals],
)
async def approve_approval(
    approval_id: UUID,
    data: ApprovalDecision,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    """
    Approve an approval request.

    Security Rules:
    - Requires: approvals.approve permission
    - Creator CANNOT approve their own requests
    - Only one approval per request

    Raises:
        PermissionDenied: If user is the creator or missing permissions
    """
    return await service.approve(approval_id, current_user, data.comment)


@router.post(
    "/{approval_id}/reject",
    response_model=ApprovalSchema,
    dependencies=[presets.CanRejectApprovals],
)
async def reject_approval(
    approval_id: UUID,
    data: ApprovalDecision,
    current_user: CurrentUserSchema = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
):
    """
    Reject an approval request.

    Security Rules:
    - Requires: approvals.reject permission
    - Creator CANNOT reject their own requests

    Raises:
        PermissionDenied: If user is the creator or missing permissions
    """
    return await service.reject(approval_id, current_user, data.comment)
