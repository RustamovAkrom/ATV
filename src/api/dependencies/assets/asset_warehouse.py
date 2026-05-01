from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db_session
from repositories.warehouse.warehouse_repo import WarehouseRepository
from services.assets.warehouse_service import WarehouseService


def get_warehouse_repo(
    db: AsyncSession = Depends(get_db_session),
) -> WarehouseRepository:
    return WarehouseRepository(db)


def get_warehouse_service(
    repo: WarehouseRepository = Depends(get_warehouse_repo),
) -> WarehouseService:
    return WarehouseService(repo)
