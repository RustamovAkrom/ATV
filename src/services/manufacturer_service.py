from uuid import UUID

from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.manufacturer import Manufacturer
from repositories.manufacturer_repo import ManufacturerRepository
from schemas.manufacturer import ManufacturerCreateSchema
from utils.validators import safe_create, validate_and_prepare


class ManufacturerService:
    def __init__(self, repo: ManufacturerRepository):
        self.repo = repo

    async def list(self):
        return await self.repo.list()

    async def create(self, data: ManufacturerCreateSchema):
        name, code = await validate_and_prepare(self.repo, data.name)

        obj = Manufacturer(
            name=name,
            code=code,
            country=data.country,
            website=str(data.website) if data.website else None,
        )

        return await safe_create(self.repo, obj)

    async def delete(self, manufacturer_id: UUID):
        obj = await self.repo.get(manufacturer_id)

        if not obj:
            raise NotFound("Manufacturer not found")

        try:
            await self.repo.delete(obj)
        except Exception as e:
            raise BadRequest("Failed to delete manufacturer") from e
