from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.user_repo import UserRepository
from services.user_service import UserService

from .rbac import RBACRepository, get_rbac_repo


def get_user_repo(
    db: AsyncSession = Depends(get_db_session)
) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repo),
    rbac_repo: RBACRepository = Depends(get_rbac_repo)
) -> UserService:
    return UserService(user_repo, rbac_repo)
