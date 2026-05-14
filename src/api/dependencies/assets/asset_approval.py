from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session


from services.approvals.approval_service import ApprovalService
from repositories.assets.approval_repo import ApprovalRepository
from services.assets.asset_service import AssetService
from services.assets.asset_transfer_service import AssetTransferService
from services.assets.repair_service import RepairService
from services.assets.asset_assignment_service import AssetAssignmentService
from services.assets.warehouse_service import WarehouseService
from core.notifications.dispatcher import NotificationDispatcher
from api.dependencies.notifications.notification import get_notification_dispatcher
from api.dependencies.assets.assets import get_asset_service
from api.dependencies.assets.asset_transfer import get_asset_transfer_service
from api.dependencies.assets.assets import get_asset_service
from api.dependencies.assets.asset_assignment import get_asset_assignment_service
from api.dependencies.assets.asset_repair import get_repair_service
from api.dependencies.warehouse import get_warehouse_service


def get_approval_repo(
    db: AsyncSession = Depends(get_db_session),
) -> ApprovalRepository:
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
    notification_dispatcher: NotificationDispatcher = Depends(
        get_notification_dispatcher
    ),
) -> ApprovalService:
    return ApprovalService(
        approval_repo,
        asset_service,
        transfer_service,
        repair_service,
        asset_assignment_service,
        warehouse_service,
        notification_dispatcher,
    )
