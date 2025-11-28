from datetime import datetime
from uuid import UUID
from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8)
    is_active: bool | None = None


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8)
