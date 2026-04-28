from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from db.models.assets.asset_history import AssetHistory


class AssetHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        asset_id: UUID,
        actor_id: UUID,
        action: str,
        description: str,
    ):
        history = AssetHistory(
            asset_id=asset_id,
            created_by_id=actor_id,
            action=action,
            description=description,
        )
        self.session.add(history)
        await self.session.flush()
        return history
