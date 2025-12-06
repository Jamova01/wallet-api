from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models import User


class RefreshToken(SQLModel, table=True):
    """Refresh token model used for session persistence and token rotation."""

    # Identifiers
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")

    # Token value
    token: str = Field(unique=True, index=True)

    # Timestamps (timezone-aware)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: Optional[datetime] = None

    # Token status / lifecycle
    revoked: bool = Field(default=False)
    revoked_at: Optional[datetime] = None

    # Relationships
    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
