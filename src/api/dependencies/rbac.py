from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.rbac_repo import RBACRepository
from services.rbac_service import RBACService


def get_rbac_repo(db: AsyncSession = Depends(get_db_session)) -> RBACRepository:
    return RBACRepository(db)


def get_rbac_service(rbac_repo: RBACRepository = Depends(get_rbac_repo)):
    return RBACService(rbac_repo)
