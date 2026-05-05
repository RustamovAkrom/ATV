from pydantic import BaseModel, ConfigDict


class StatusResponse(BaseModel):
    status: str
    message: str | None

    model_config = ConfigDict(from_attributes=True)
