from uuid import UUID, uuid4
from typing import TYPE_CHECKING, List
from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr


if TYPE_CHECKING:
    from app.models import RefreshToken


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)

    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user")
