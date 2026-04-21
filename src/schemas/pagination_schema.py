from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParamsSchema(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)

    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PageSchema(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(arbitrary_types_allowed=True)
