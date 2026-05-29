from math import ceil
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, computed_field

T = TypeVar("T")


class PaginationParamsSchema(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    sort_by: str | None = Field(None, description="Sort field")
    sort_desc: bool = Field(False, description="Sort descending")

    def offset(self) -> int:
        return (self.page - 1) * self.limit

    @computed_field
    @property
    def skip(self) -> int:
        """Alias for offset"""
        return self.offset()


class PageSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


class PageOutSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @computed_field
    @property
    def pages(self) -> int:
        """Total number of pages"""
        return ceil(self.total / self.limit) if self.total > 0 else 1

    @computed_field
    @property
    def has_next(self) -> bool:
        """Check if next page exists"""
        return self.page < self.pages

    @computed_field
    @property
    def has_prev(self) -> bool:
        """Check if previous page exists"""
        return self.page > 1


SimplePage = PageOutSchema
