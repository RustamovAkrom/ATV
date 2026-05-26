from uuid import UUID
from typing import List
from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.asset_class import AssetClass
from repositories.assets.asset_class_repo import AssetClassRepository
from schemas.assets.asset_class import AssetClassCreateSchema, AssetClassOutSchema
from utils.validators import safe_create, validate_and_prepare


class AssetClassService:
    def __init__(self, repo: AssetClassRepository):
        self.repo = repo

    async def list(self) -> List[AssetClassOutSchema]:
        return await self.repo.list()

    async def create(self, data: AssetClassCreateSchema):
        obj = AssetClass(
            name=data.name,
            description=data.description,
        )

        return await safe_create(self.repo, obj)

    async def delete(self, class_id: UUID) -> None:
        obj = await self.repo.get(class_id)

        if not obj:
            raise NotFound("Asset class not found")

        try:
            await self.repo.delete(obj)
        except Exception as e:
            raise BadRequest("Failed to delete asset class") from e
