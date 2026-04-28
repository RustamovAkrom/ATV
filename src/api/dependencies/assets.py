from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.approval_repo import ApprovalRepository
from repositories.assets.asset_assignment_repo import AssetAssignmentRepository
from repositories.assets.asset_repo import AssetRepository
from repositories.assets.asset_transfer_repo import AssetTransferRepository
from repositories.documents.document_repo import DocumentRepository
from repositories.assets.repair_repo import RepairRepository
from repositories.warehouse.warehouse_repo import WarehouseRepository
from services.approvals.approval_service import ApprovalService
from services.assets.asset_assignment_service import AssetAssignmentService
from services.assets.asset_history_service import AssetHistoryService
from services.assets.asset_service import AssetService
from services.assets.asset_transfer_service import AssetTransferService
from services.assets.bulk_asset_service import BulkAssetService
from services.documents.document_service import DocumentService
from services.assets.export_service import ExportService
from services.assets.repair_service import RepairService
from services.assets.warehouse_service import WarehouseService
from core.notifications.dispatcher import NotificationDispatcher
from api.dependencies.notifications import (
    get_notification_dispatcher,
    get_notification_service,
)


def get_asset_history_service(
    db: AsyncSession = Depends(get_db_session),
) -> AssetHistoryService:
    return AssetHistoryService(db)


def get_asset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetRepository:
    return AssetRepository(db)


def get_asset_service(
    asset_repo: AssetRepository = Depends(get_asset_repo),
    notification_dispatcher: NotificationDispatcher = Depends(
        get_notification_dispatcher
    ),
) -> AssetService:
    return AssetService(asset_repo, notification_dispatcher)


def get_export_service(
    asset_repo: AssetRepository = Depends(get_asset_repo),
) -> ExportService:
    return ExportService(asset_repo)


def get_asset_assignment_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetAssignmentRepository:
    return AssetAssignmentRepository(db)


def get_asset_assignment_service(
    repo: AssetAssignmentRepository = Depends(get_asset_assignment_repo),
) -> AssetAssignmentService:
    return AssetAssignmentService(repo)


def get_asset_transfer_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetTransferRepository:
    return AssetTransferRepository(db)


def get_asset_transfer_service(
    repo: AssetTransferRepository = Depends(get_asset_transfer_repo),
) -> AssetTransferService:
    return AssetTransferService(repo)


def get_repair_repo(
    db: AsyncSession = Depends(get_db_session),
) -> RepairRepository:
    return RepairRepository(db)


def get_repair_service(
    repo: RepairRepository = Depends(get_repair_repo),
) -> RepairService:
    return RepairService(repo)


def get_document_repo(
    db: AsyncSession = Depends(get_db_session),
) -> DocumentRepository:
    return DocumentRepository(db)


def get_document_service(
    repo: DocumentRepository = Depends(get_document_repo),
) -> DocumentService:
    return DocumentService(repo)


def get_warehouse_repo(
    db: AsyncSession = Depends(get_db_session),
) -> WarehouseRepository:
    return WarehouseRepository(db)


def get_warehouse_service(
    repo: WarehouseRepository = Depends(get_warehouse_repo),
) -> WarehouseService:
    return WarehouseService(repo)


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
        notification_dispatcher,
    )


def get_bulk_asset_service(
    db: AsyncSession = Depends(get_db_session),
    assignment_service: AssetAssignmentService = Depends(get_asset_assignment_service),
    transfer_service: AssetTransferService = Depends(get_asset_transfer_service),
    asset_service: AssetService = Depends(get_asset_service),
) -> BulkAssetService:
    return BulkAssetService(db, assignment_service, transfer_service, asset_service)
