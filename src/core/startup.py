from core.database import get_session_factory
from scripts.seed import seed_all


async def run_seed() -> None:
    session_factory = get_session_factory()
    async with session_factory() as db:
        await seed_all(db)
        await db.commit()
