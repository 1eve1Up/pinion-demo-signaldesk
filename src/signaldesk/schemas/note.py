from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

InteractionType = Literal["call", "meeting", "follow_up", "other"]


class NoteCreate(BaseModel):
    body: str = Field(min_length=1)
    interaction_type: InteractionType | None = None
    occurred_at: datetime | None = None

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_must_be_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware (include offset or Z)")
        return v


class NoteUpdate(BaseModel):
    body: str | None = Field(default=None, min_length=1)
    interaction_type: InteractionType | None = None
    occurred_at: datetime | None = None

    @field_validator("occurred_at")
    @classmethod
    def occurred_at_must_be_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware (include offset or Z)")
        return v


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    body: str
    interaction_type: str | None
    occurred_at: datetime | None
    created_at: datetime
    updated_at: datetime
