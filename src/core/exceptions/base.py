# src/core/exceptions/base.py

from typing import Any


class APIException(Exception):
    """
    Base API exception for all controlled errors.
    """

    status_code: int = 400
    code: str = "error"
    detail: str = "Something went wrong."

    def __init__(
        self,
        detail: str | None = None,
        *,
        code: str | None = None,
        values: dict[str, Any] | None = None,
        status_code: int | None = None,
    ) -> None:

        self.detail = detail or self.detail
        self.code = code or self.code
        self.status_code = status_code or self.status_code

        self.values: dict[str, Any] = values or {}

        super().__init__(self.detail)

    def to_dict(self, trace_id: str | None = None) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.detail,
                "details": self.values,
                "trace_id": trace_id,
            }
        }
