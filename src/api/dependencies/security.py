from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.dependencies import get_db_session

from services.security_service import SecurityService
from repositories.password_reset_repo import PasswordResetRepository
from repositories.user_repo import UserRepository
from repositories.auth_repo import AuthRepository
from .users import get_user_repo
from .auth import get_auth_repo


def get_reset_repo(
    db: AsyncSession = Depends(get_db_session),
) -> PasswordResetRepository:
    return PasswordResetRepository(db)


def get_security_service(
    user_repo: UserRepository = Depends(get_user_repo),
    auth_repo: AuthRepository = Depends(get_auth_repo),
    reset_repo: PasswordResetRepository = Depends(get_reset_repo)
) -> SecurityService:
    return SecurityService(user_repo, auth_repo, reset_repo)
