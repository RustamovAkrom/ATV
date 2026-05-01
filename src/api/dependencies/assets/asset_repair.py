from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.repair_repo import RepairRepository
from services.assets.repair_service import RepairService
from api.dependencies.events.asset_repair import get_asset_repair_event_service


def get_repair_repo(
    db: AsyncSession = Depends(get_db_session),
) -> RepairRepository:
    return RepairRepository(db)


def get_repair_service(
    repo: RepairRepository = Depends(get_repair_repo),
    repair_events: RepairService = Depends(get_asset_repair_event_service),
) -> RepairService:
    return RepairService(
        repo,
        repair_events,
    )
