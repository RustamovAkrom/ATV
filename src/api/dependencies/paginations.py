from typing import Annotated

from fastapi.params import Query

from schemas.pagination import PaginationParamsSchema


def get_pagination(
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return PaginationParamsSchema(
        page=page,
        limit=limit,
        sort_by=None,
        sort_desc=False,
    )
