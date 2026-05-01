from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.asset_assignment_repo import AssetAssignmentRepository
from services.assets.asset_assignment_service import AssetAssignmentService
from core.events.asset_events import AssetEventService
from api.dependencies.events.asset import get_asset_event_service


def get_asset_assignment_repo(
    db: AsyncSession = Depends(get_db_session),
) -> AssetAssignmentRepository:
    return AssetAssignmentRepository(db)


def get_asset_assignment_service(
    repo: AssetAssignmentRepository = Depends(get_asset_assignment_repo),
    events: AssetEventService = Depends(get_asset_event_service),
) -> AssetAssignmentService:
    return AssetAssignmentService(repo, events)
