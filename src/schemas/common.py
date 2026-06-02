from pydantic import ConfigDict, Field

from schemas.base import BaseResponseSchema


class StatusResponse(BaseResponseSchema):
    status: str = Field(
        ...,
        pattern=r"^(success|error|ok|archived|active|blocked|deleted|created|updated)$",
    )
    message: str | None = Field(None, max_length=500)

    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseResponseSchema):
    """Standard error response"""

    error: str
    message: str
    code: str | None = None
    trace_id: str | None = None

class MessageResponse(BaseResponseSchema):
    """Simple message response"""

    message: str
