from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    body: str = Field(min_length=1)


class NoteUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1)


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    body: str
    created_at: datetime
    updated_at: datetime
