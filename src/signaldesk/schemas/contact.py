from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company: str | None = Field(default=None, max_length=255)


class ContactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    name: str
    email: str | None
    phone: str | None
    company: str | None
    created_at: datetime
    updated_at: datetime
