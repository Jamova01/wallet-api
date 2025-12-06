from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def _expiration(delta: timedelta) -> datetime:
    """Return UTC expiration datetime."""
    return datetime.now(timezone.utc) + delta


def _create_token(
    subject: str | Any,
    expires: datetime,
    secret_key: str,
    algorithm: str,
) -> str:
    payload = {
        "sub": str(subject),
        "exp": expires,
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def create_access_token(
    subject: str | Any,
    expires_minutes: int | None = None,
) -> str:
    minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expires = _expiration(timedelta(minutes=minutes))

    return _create_token(
        subject,
        expires,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )


def create_refresh_token(
    subject: str | Any,
    expires_days: int | None = None,
) -> str:
    days = expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    expires = _expiration(timedelta(days=days))

    return _create_token(
        subject,
        expires,
        settings.REFRESH_SECRET_KEY,
        settings.ALGORITHM,
    )
