from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.approval_repo import ApprovalRepository
from repositories.asset_assignment_repo import AssetAssignmentRepository
from repositories.asset_repo import AssetRepository
from repositories.asset_transfer_repo import AssetTransferRepository
from repositories.document_repo import DocumentRepository
from repositories.repair_repo import RepairRepository
from repositories.warehouse_repo import WarehouseRepository
from services.approval_service import ApprovalService
from services.asset_assignment_service import AssetAssignmentService
from services.asset_service import AssetService
from services.asset_transfer_service import AssetTransferService
from services.bulk_asset_service import BulkAssetService
from services.document_service import DocumentService
from services.export_service import ExportService
from services.repair_service import RepairService
from services.warehouse_service import WarehouseService


def get_asset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetRepository:
    return AssetRepository(db)


def get_asset_service(
    asset_repo: AssetRepository = Depends(get_asset_repo),
) -> AssetService:
    return AssetService(asset_repo)


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
) -> ApprovalService:
    return ApprovalService(approval_repo, asset_service, transfer_service, repair_service)


def get_bulk_asset_service(
    db: AsyncSession = Depends(get_db_session),
    assignment_service: AssetAssignmentService = Depends(get_asset_assignment_service),
    transfer_service: AssetTransferService = Depends(get_asset_transfer_service),
    asset_service: AssetService = Depends(get_asset_service),
) -> BulkAssetService:
    return BulkAssetService(db, assignment_service, transfer_service, asset_service)
