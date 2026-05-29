from pydantic import BaseModel, ConfigDict, Field


class StatusResponse(BaseModel):
    status: str = Field(
        ...,
        pattern=r"^(success|error|ok|archived|active|blocked|deleted|created|updated)$",  # Добавил 'deleted', 'created', 'updated'
    )
    message: str | None = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)


class ErrorResponse(BaseModel):
    """Стандартный ответ с ошибкой"""

    error: str
    message: str
    code: str | None = None
    trace_id: str | None = None


class MessageResponse(BaseModel):
    """Простой ответ с сообщением"""

    message: str
