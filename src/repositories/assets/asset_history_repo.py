from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from core.exceptions.errors import Conflict

from db.models.assets.asset_history import AssetHistory
from repositories.base import BaseRepository


class AssetHistoryRepository(BaseRepository):
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
        self.add(history)
        await self.flush()
        return history
