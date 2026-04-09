from typing import Any


class APIException(Exception):
    """
    Base API exception.
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
        if detail:
            self.detail = detail

        if code:
            self.code = code

        if status_code:
            self.status_code = status_code

        self.values: dict[str, Any] = values or {}

        super().__init__(self.detail)
