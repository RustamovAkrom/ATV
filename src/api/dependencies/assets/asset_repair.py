from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.events.asset_repair import get_repair_event_service
from core.events.repair_events import RepairEventService
from db.dependencies import get_db_session
from repositories.assets.repair_repo import RepairRepository
from services.assets.repair_service import RepairService


def get_repair_repo(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RepairRepository:
    return RepairRepository(db)


def get_repair_service(
    repo: Annotated[RepairRepository, Depends(get_repair_repo)],
    repair_events: Annotated[RepairEventService, Depends(get_repair_event_service)],
) -> RepairService:
    return RepairService(
        repo,
        repair_events,
    )
