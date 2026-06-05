from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.organization.department_repo import DepartmentRepository
from services.organization.department_service import DepartmentService


def get_department_repo(
    db: AsyncSession = Depends(get_db_session),
) -> DepartmentRepository:
    return DepartmentRepository(db)


def get_department_service(
    repo: DepartmentRepository = Depends(get_department_repo),
) -> DepartmentService:
    return DepartmentService(repo)
