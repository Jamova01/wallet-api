"""Authentication service providing login, signup and token management."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.security import verify_password
from app.models.token import RefreshToken
from app.models.user import User
from app.schemas.auth import SignupRequest, Token
from app.schemas.user import UserCreate
from app.services import user_service


# ---------------------------------------------------------------------------
# Authentication / Login
# ---------------------------------------------------------------------------


def authenticate(session: Session, email: str, password: str) -> Optional[User]:
    """
    Verify a user's credentials by email and password.

    Args:
        session (Session): The database session to use.
        email (str): User's email address.
        password (str): Plain text password to verify.

    Returns:
        Optional[User]: The User instance if credentials are valid, else None.
    """
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def login(session: Session, email: str, password: str) -> Token:
    """
    Authenticate user and issue both access and refresh tokens.

    Args:
        session (Session): The database session to use.
        email (str): User's email address.
        password (str): Plain text password.

    Returns:
        Token: An object containing `access_token` and `refresh_token`.

    Raises:
        HTTPException: If credentials are invalid or user is inactive.
    """
    user = authenticate(session=session, email=email, password=password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access = create_access_token(user_id=user.id)
    refresh_record = create_refresh_token_record(session=session, user_id=user.id)

    return Token(access_token=access, refresh_token=refresh_record.token)


# ---------------------------------------------------------------------------
# User Registration
# ---------------------------------------------------------------------------


def signup(session: Session, payload: SignupRequest) -> User:
    """
    Register a new user in the system.

    Args:
        session (Session): The database session to use.
        payload (SignupRequest): Data required for user creation.

    Returns:
        User: The newly created user instance.

    Raises:
        HTTPException: If a user with the same email already exists.
    """
    existing_user = user_service.get_user_by_email(
        session=session,
        email=payload.email,
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user_data = UserCreate.model_validate(payload)
    return user_service.create(session=session, user_data=user_data)


# ---------------------------------------------------------------------------
# Token Management
# ---------------------------------------------------------------------------


def create_access_token(user_id: int) -> str:
    """
    Generate a new JWT access token for a user.

    Args:
        user_id (int): Identifier of the user.

    Returns:
        str: A signed JWT access token.
    """
    return security.create_access_token(subject=user_id)


def create_refresh_token_record(session: Session, user_id: int) -> RefreshToken:
    """
    Create and persist a new refresh token for a user.

    Args:
        session (Session): The database session to use.
        user_id (int): Identifier of the user.

    Returns:
        RefreshToken: The database record for the new refresh token.
    """
    raw_token = security.create_refresh_token(subject=user_id)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    token_record = RefreshToken(
        user_id=user_id,
        token=raw_token,
        expires_at=expires_at,
    )
    session.add(token_record)
    session.commit()
    session.refresh(token_record)
    return token_record


def validate_refresh_token(session: Session, token: str) -> Optional[RefreshToken]:
    """
    Validate a refresh token: existence, non-revoked and not expired.

    Args:
        session (Session): The database session to use.
        token (str): Refresh token string provided by the client.

    Returns:
        Optional[RefreshToken]: The token record if valid, else None.
    """
    record = session.exec(
        select(RefreshToken).where(RefreshToken.token == token)
    ).first()
    if not record:
        return None

    if getattr(record, "revoked", False):
        return None

    # Ensure expires_at is timezone-aware
    if record.expires_at.tzinfo is None:
        record.expires_at = record.expires_at.replace(tzinfo=timezone.utc)

    if record.expires_at < datetime.now(timezone.utc):
        return None

    return record


def revoke_refresh_token(session: Session, token_record: RefreshToken) -> None:
    """
    Revoke a refresh token so it can no longer be used.

    Args:
        session (Session): The database session to use.
        token_record (RefreshToken): The token record to revoke.
    """
    token_record.revoked = True
    session.add(token_record)
    session.commit()


def refresh(session: Session, refresh_token: str) -> Token:
    """
    Refresh access token using a valid refresh token.

    Validates the provided refresh token, updates its last-used timestamp,
    and issues a new access token. The existing refresh token remains valid.

    Args:
        session (Session): The database session to use.
        refresh_token (str): The refresh token string provided by the client.

    Returns:
        Token: An object containing the new access token and the same
        refresh token.

    Raises:
        HTTPException: If the refresh token is invalid, expired, or revoked.
    """
    record = validate_refresh_token(session=session, token=refresh_token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    record.last_used_at = datetime.now(timezone.utc)
    session.add(record)
    session.commit()

    new_access = create_access_token(user_id=record.user_id)
    return Token(access_token=new_access, refresh_token=record.token)
