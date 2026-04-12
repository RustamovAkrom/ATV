# src/scripts/cleanup/tokens.py

from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.refresh_token import RefreshToken
from core.database import get_session_factory


BATCH_SIZE = 1000


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Delete expired refresh tokens in batches.

    Returns:
        int: number of deleted rows
    """

    total_deleted = 0

    while True:
        # 🔥 берём batch id-шников
        result = await db.execute(
            select(RefreshToken.id)
            .where(RefreshToken.expires_at < datetime.utcnow())
            .limit(BATCH_SIZE)
        )
        ids = result.scalars().all()

        if not ids:
            break

        # 🔥 удаляем batch
        await db.execute(
            delete(RefreshToken).where(RefreshToken.id.in_(ids))
        )

        total_deleted += len(ids)

        # 🔥 flush чтобы не копился state
        await db.flush()

    return total_deleted


# -----------------------
# RUNNER (для Taskfile)
# -----------------------

async def _run():
    session_factory = get_session_factory()

    async with session_factory() as session:
        async with session.begin():
            deleted = await cleanup_expired_tokens(session)

    print(f"🧹 Deleted {deleted} expired refresh tokens")


def run():
    import asyncio
    asyncio.run(_run())
