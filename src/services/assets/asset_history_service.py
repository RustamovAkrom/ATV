from uuid import UUID

from core.exceptions.errors import NotFound
from core.security.access_control import AccessControl
from db.models.assets.asset import Asset
from repositories.assets.asset_history_repo import AssetHistoryRepository
from schemas.assets.assets import AssetHistorySchema
from schemas.auth.auth import CurrentUserSchema


class AssetHistoryService:
    def __init__(self, repo: AssetHistoryRepository):
        self.repo = repo

    async def log(
        self,
        asset_id: UUID,
        actor_id: UUID,
        action: str,
        description: str,
    ):
        return await self.repo.create(
            asset_id=asset_id,
            actor_id=actor_id,
            action=action,
            description=description,
        )
