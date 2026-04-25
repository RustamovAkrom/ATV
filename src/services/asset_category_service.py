import re

from sqlalchemy.exc import IntegrityError
from core.exceptions.errors import NotFound, BadRequest
from db.models.assets.asset_category import AssetCategory
from repositories.asset_category_repo import AssetCategoryRepository
from schemas.asset_category import AssetCategoryCreateSchema
from utils.validators import validate_and_prepare, safe_create


class AssetCategoryService:
    def __init__(self, repo: AssetCategoryRepository):
        self.repo = repo

    async def list(self):
        return await self.repo.list()

    async def create(self, data: AssetCategoryCreateSchema):
        name, code = await validate_and_prepare(self.repo, data.name)

        obj = AssetCategory(
            name=name,
            code=code,
        )

        return await safe_create(self.repo, obj)

    async def delete(self, category_id):
        obj = await self.repo.get(category_id)
        if not obj:
            raise NotFound("Category not found")
        try:
            await self.repo.delete(obj)
        except Exception:
            raise BadRequest("Failed to delete category")
