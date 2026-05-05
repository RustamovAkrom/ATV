from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.organization.service_repo import ServiceRepository
from services.organization.service_service import ServiceService


def get_service_repo(db: AsyncSession = Depends(get_db_session)) -> ServiceRepository:
    return ServiceRepository(db)


def get_service_service(
    repo: ServiceRepository = Depends(get_service_repo),
) -> ServiceService:
    return ServiceService(repo)
