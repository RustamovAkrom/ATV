from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.pagination import Page, PaginationParams


async def paginate(db: AsyncSession, query, pagination: PaginationParams):
    limit = min(pagination.limit, 100)
    offset = pagination.offset()

    total = await db.scalar(
        select(func.count()).select_from(query.order_by(None).subquery())
    )

    result = await db.execute(
        query.limit(limit).offset(offset)
    )
    items = result.scalars().all()

    return Page(
        items=items,
        total=total or 0,
        page=pagination.page,
        limit=limit,
    )
