from math import ceil
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParamsSchema(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PageSchema(BaseModel):
    items: list[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PageMetaSchema(BaseModel):
    pages: int
    has_next: bool
    has_prev: bool


class PageOutSchema(PageMetaSchema):
    items: list[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


def build_page(
    *,
    schema,
    items: list[Any],
    total: int,
    page: int,
    limit: int,
    aggregates: Any | None = None,
):
    pages = ceil(total / limit) if total > 0 else 1

    return schema(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
        aggregates=aggregates,
    )
