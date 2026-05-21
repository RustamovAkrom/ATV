from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.asset_transfer_repo import AssetTransferRepository
from services.assets.asset_transfer_service import AssetTransferService
from core.events.transfer_events import TransferEventService
from api.dependencies.events.asset_transfer import get_transfer_event_service


def get_asset_transfer_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetTransferRepository:
    return AssetTransferRepository(db)


def get_asset_transfer_service(
    repo: AssetTransferRepository = Depends(get_asset_transfer_repo),
    transfer_events: TransferEventService = Depends(get_transfer_event_service),
) -> AssetTransferService:
    return AssetTransferService(
        repo,
        transfer_events=transfer_events,
    )
