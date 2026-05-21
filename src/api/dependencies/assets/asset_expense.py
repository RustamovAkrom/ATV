from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.assets.expense_repo import ExpenseRepository
from services.assets.expense_service import ExpenseService


def get_expense_repo(
    db: AsyncSession = Depends(get_db_session),
) -> ExpenseRepository:
    return ExpenseRepository(db)


def get_expense_service(
    repo: ExpenseRepository = Depends(get_expense_repo),
) -> ExpenseService:
    return ExpenseService(repo)
