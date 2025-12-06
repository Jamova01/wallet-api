from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class SignupRequest(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class RefreshTokenRequest(SQLModel):
    refresh_token: str
