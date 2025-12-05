from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from app.models import User


class RefreshToken(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")

    # JWT token string
    token: str = Field(unique=True, index=True)

    # Timestamps - ensure all are timezone-aware
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: Optional[datetime] = None

    # Token status
    revoked: bool = Field(default=False)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
