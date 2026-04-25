from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session_factory
from db.models.refresh_token import RefreshToken


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    result = await db.execute(
        delete(RefreshToken).where(RefreshToken.expires_at < datetime.now(timezone.utc))
    )

    return result.rowcount or 0


# -----------------------
# RUNNER
# -----------------------
async def _run():
    session_factory = get_session_factory()

    async with session_factory() as session:
        async with session.begin():
            deleted = await cleanup_expired_tokens(session)

    print(f"🧹 Deleted {deleted} expired tokens")


def run():
    import asyncio

    asyncio.run(_run())
