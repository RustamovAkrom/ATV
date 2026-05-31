from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.assets.asset import get_asset_service
from api.dependencies.assets.asset_assignment import get_asset_assignment_service
from api.dependencies.assets.asset_repair import get_repair_service
from api.dependencies.assets.asset_transfer import get_asset_transfer_service
from api.dependencies.assets.asset_warehouse import get_warehouse_service
from api.dependencies.events.approval import get_approval_event_service
from core.events.approval_events import ApprovalEventService
from db.dependencies import get_db_session
from repositories.assets.approval_repo import ApprovalRepository
from services.approvals.approval_service import ApprovalService
from services.assets.asset_assignment_service import AssetAssignmentService
from services.assets.asset_service import AssetService
from services.assets.asset_transfer_service import AssetTransferService
from services.assets.repair_service import RepairService
from services.assets.warehouse_service import WarehouseService


def get_approval_repo(
    db: AsyncSession = Depends(get_db_session),
) -> ApprovalRepository:
    """Get approval repository."""
    return ApprovalRepository(db)


def get_approval_service(
    approval_repo: ApprovalRepository = Depends(get_approval_repo),
    asset_service: AssetService = Depends(get_asset_service),
    transfer_service: AssetTransferService = Depends(get_asset_transfer_service),
    repair_service: RepairService = Depends(get_repair_service),
    asset_assignment_service: AssetAssignmentService = Depends(
        get_asset_assignment_service
    ),
    warehouse_service: WarehouseService = Depends(get_warehouse_service),
    approval_events: ApprovalEventService = Depends(get_approval_event_service),
) -> ApprovalService:
    """Get approval service with all dependencies."""
    return ApprovalService(
        approval_repo=approval_repo,
        asset_service=asset_service,
        transfer_service=transfer_service,
        repair_service=repair_service,
        asset_assignment_service=asset_assignment_service,
        warehouse_service=warehouse_service,
        approval_events=approval_events,
    )
