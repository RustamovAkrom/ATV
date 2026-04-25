# services/asset_model_service.py

from uuid import UUID

from core.exceptions.errors import NotFound, BadRequest
from db.models.assets.asset_model import AssetModel

from repositories.asset_model_repo import AssetModelRepository
from repositories.manufacturer_repo import ManufacturerRepository
from repositories.asset_category_repo import AssetCategoryRepository
from schemas.asset_model import AssetModelCreateSchema
from utils.validators import (
    validate_name,
    normalize_name,
    ensure_unique_code,
    safe_create,
)
from utils.slug import slugify


class AssetModelService:
    def __init__(self,
            repo: AssetModelRepository,
            manufacturer_repo: ManufacturerRepository,
            category_repo: AssetCategoryRepository,
    ):
        self.repo = repo
        self.manufacturer_repo = manufacturer_repo
        self.category_repo = category_repo

    async def list(self):
        return await self.repo.list()

    async def create(self, data: AssetModelCreateSchema):
        # 1. validate name
        name = validate_name(data.name)
        normalized = normalize_name(name)

        # 2. check duplicate (ВАЖНО: с manufacturer)
        existing = await self.repo.get_by_name_and_manufacturer(
            normalized,
            data.manufacturer_id
        )
        if existing:
            raise BadRequest("Model already exists for this manufacturer")

        # 3. slug
        code = slugify(name)
        if not code:
            raise BadRequest("Invalid name")

        # 4. check code (global)
        await ensure_unique_code(self.repo, code)

        # 5. FK checks
        manufacturer = await self.manufacturer_repo.get(data.manufacturer_id)
        if not manufacturer:
            raise BadRequest("Manufacturer not found")

        category = await self.category_repo.get(data.category_id)
        if not category:
            raise BadRequest("Category not found")

        # 6. create
        obj = AssetModel(
            name=name,
            code=code,
            manufacturer_id=data.manufacturer_id,
            category_id=data.category_id,
            lifetime_years=data.lifetime_years,
            warranty_months=data.warranty_months,
        )

        return await safe_create(self.repo, obj)

    async def delete(self, model_id: UUID):
        obj = await self.repo.get(model_id)

        if not obj:
            raise NotFound("Model not found")

        try:
            await self.repo.delete(obj)
        except Exception:
            raise BadRequest("Failed to delete model")
