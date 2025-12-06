from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models import RefreshToken


class User(SQLModel, table=True):
    """
    Database model representing an application user.

    Stores authentication fields, role flags, and timestamp metadata.
    """

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(
        default=True, description="Indicates if the user can log in."
    )
    is_superuser: bool = Field(
        default=False, description="Flag for elevated permissions."
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the user was created.",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the user was last updated.",
    )

    # Relationships
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
