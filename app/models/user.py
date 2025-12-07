from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models import RefreshToken
    from app.models.account import Account


class User(SQLModel, table=True):
    """
    Represents a user of the application.

    This model stores authentication credentials, user status, role flags,
    and timestamp metadata. It also defines relationships to refresh tokens
    and financial accounts.

    Attributes:
        id (UUID):
            Unique identifier for the user.
        email (EmailStr):
            User's email address, must be unique and indexed.
        hashed_password (str):
            Hashed version of the user's password.
        is_active (bool):
            Indicates whether the user can log in. Default is True.
        is_superuser (bool):
            Flag indicating elevated permissions. Default is False.
        created_at (datetime):
            Timestamp when the user was created (UTC).
        updated_at (datetime):
            Timestamp when the user was last updated (UTC).
        refresh_tokens (List[RefreshToken]):
            List of refresh tokens issued to the user.
        accounts (List[Account]):
            List of financial accounts associated with the user.
    """

    # Primary fields
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str

    # Status and role flags
    is_active: bool = Field(
        default=True, description="Indicates if the user can log in."
    )
    is_superuser: bool = Field(
        default=False, description="Flag for elevated permissions."
    )

    # Timestamps
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
    accounts: List["Account"] = Relationship(back_populates="user")
