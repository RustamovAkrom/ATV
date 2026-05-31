from typing import Annotated

from fastapi.params import Depends

from api.dependencies.assets.asset import get_asset_repo
from repositories.assets.asset_repo import AssetRepository
from services.assets.export_service import ExportService


def get_export_service(
    asset_repo: Annotated[AssetRepository, Depends(get_asset_repo)],
) -> ExportService:
    return ExportService(asset_repo)
