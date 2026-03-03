from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Knowledge(BaseModel):
    expiration_date: datetime | None = Field(
        description="The expiration date of the knowledge. Can be None if the knowledge does not expire."
    )
    information: str = Field(description="Short and concise piece of information.")
    uuid: UUID | None = Field(description="ID of the knowledge piece.")
