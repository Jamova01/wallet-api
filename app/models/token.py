from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Relationship, SQLModel, Field

from app.models.user import User


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    token: str = Field(nullable=False, unique=True, index=True)
    revoked: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=datetime.now(timezone.utc), nullable=False
    )
    expires_at: datetime = Field(nullable=False)

    user: Optional["User"] = Relationship(back_populates="refresh_tokens")
