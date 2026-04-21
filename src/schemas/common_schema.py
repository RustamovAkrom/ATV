from typing import Optional

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str
    message: Optional[str]
