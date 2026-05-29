from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.db_async import get_async_session_factory
from db.models.refresh_token import RefreshToken
from db.models.users.user import User  # noqa: F401 - импортируем для инициализации relationship


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    result = await db.execute(
        delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(UTC))
    )

    return result.rowcount or 0


# -----------------------
# RUNNER
# -----------------------
async def _run():
    session_factory = get_async_session_factory()

    async with session_factory() as session:
        async with session.begin():
            deleted = await cleanup_expired_tokens(session)

    print(f"Deleted {deleted} expired tokens")


def run():
    import asyncio

    asyncio.run(_run())
