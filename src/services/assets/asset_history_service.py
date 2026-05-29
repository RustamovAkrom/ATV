from uuid import UUID

from repositories.assets.asset_history_repo import AssetHistoryRepository


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
