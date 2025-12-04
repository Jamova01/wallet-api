from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Security
    ALGORITHM: str = "HS256"
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str

    # Token expiration
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API
    API_V1_STR: str = "/api/v1"

    # Initial superuser
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str


settings = Settings()
