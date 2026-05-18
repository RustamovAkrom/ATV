from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.asset_repo import AssetRepository
from services.assets.asset_assignment_service import AssetAssignmentService
from services.assets.asset_service import AssetService
from services.assets.asset_transfer_service import AssetTransferService
from services.assets.bulk_asset_service import BulkAssetService
from core.events.asset_events import AssetEventService
from api.dependencies.events.asset import get_asset_event_service
from api.dependencies.assets.asset_assignment import get_asset_assignment_service
from api.dependencies.assets.asset_transfer import get_asset_transfer_service


def get_asset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetRepository:
    return AssetRepository(db)


def get_asset_service(
    asset_repo: AssetRepository = Depends(get_asset_repo),
    asset_events: AssetEventService = Depends(get_asset_event_service),
) -> AssetService:
    return AssetService(asset_repo, asset_events)


def get_bulk_asset_service(
    db: AsyncSession = Depends(get_db_session),
    assignment_service: AssetAssignmentService = Depends(get_asset_assignment_service),
    transfer_service: AssetTransferService = Depends(get_asset_transfer_service),
    asset_service: AssetService = Depends(get_asset_service),
) -> BulkAssetService:
    return BulkAssetService(db, assignment_service, transfer_service, asset_service)
