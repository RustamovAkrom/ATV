from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.asset_category import AssetCategory
from repositories.assets.asset_category_repo import AssetCategoryRepository
from schemas.assets.asset_category import AssetCategoryCreateSchema
from utils.validators import safe_create, validate_and_prepare


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
        except Exception as e:
            raise BadRequest("Failed to delete category") from e
