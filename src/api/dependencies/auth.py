from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.auth.auth_repo import AuthRepository
from repositories.users.user_repo import UserRepository
from services.auth.auth_service import AuthService

from .users import get_user_repo


def get_auth_repo(db: AsyncSession = Depends(get_db_session)) -> AuthRepository:
    return AuthRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    auth_repo: AuthRepository = Depends(get_auth_repo),
) -> AuthService:
    return AuthService(user_repo, auth_repo)
