from fastapi.params import Query

from schemas.pagination import PaginationParamsSchema


def get_pagination(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    return PaginationParamsSchema(page=page, limit=limit)
