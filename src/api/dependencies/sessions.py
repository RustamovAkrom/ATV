from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.session_repo import SessionRepository
from services.session_service import SessionService


def get_session_repo(db: AsyncSession = Depends(get_db_session)):
    return SessionRepository(db)


def get_session_service(
    session_repo: SessionRepository = Depends(get_session_repo)
) -> SessionService:
    return SessionService(session_repo)
