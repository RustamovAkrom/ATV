# services/asset_class_service.py

from uuid import UUID

from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.asset_class import AssetClass
from repositories.asset_class_repo import AssetClassRepository
from schemas.asset_class import AssetClassCreateSchema, AssetClassOutSchema
from utils.validators import safe_create, validate_and_prepare


class AssetClassService:
    def __init__(self, repo: AssetClassRepository):
        self.repo = repo

    async def list(self) -> list[AssetClassOutSchema]:
        return await self.repo.list()

    async def create(self, data: AssetClassCreateSchema):
        name, code = await validate_and_prepare(self.repo, data.name)

        obj = AssetClass(
            name=name,
            code=code,
            description=data.description,
        )

        return await safe_create(self.repo, obj)

    async def delete(self, class_id: UUID):
        obj = await self.repo.get(class_id)

        if not obj:
            raise NotFound("Asset class not found")

        try:
            await self.repo.delete(obj)
        except Exception:
            raise BadRequest("Failed to delete asset class")
