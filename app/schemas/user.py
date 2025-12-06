from datetime import datetime
from uuid import UUID
from pydantic import EmailStr
from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    """
    Shared fields for user-related schemas.
    """

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)


class UserCreate(UserBase):
    """
    Schema used for user registration.

    Includes the required plaintext password field.
    """

    password: str = Field(min_length=8)


class UserRead(UserBase):
    """
    Schema returned when reading user data.

    Contains read-only fields like ID and timestamps.
    """

    id: UUID
    created_at: datetime
    updated_at: datetime


class UserUpdate(UserBase):
    """
    Admin-level user update schema.

    Allows partial updates of email and password.
    """

    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8)


class UserUpdateMe(SQLModel):
    """
    Schema for updating the current logged-in user (self).

    Does not allow privilege changes.
    """

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """
    Schema to update the user's password.

    Enforces basic password length and provides both
    current and new password fields.
    """

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
