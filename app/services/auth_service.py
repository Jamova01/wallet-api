"""Authentication service for handling login, signup, logout, and token management.

This module centralizes the business logic for user authentication:
- Credential validation
- Access and refresh token issuance
- Refresh token persistence, validation, and revocation
- User registration

The routing layer delegates all security-related logic to this service.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

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
    """Validate a user's credentials.

    Args:
        session (Session): Database session to use.
        email (str): User's email address.
        password (str): Plain-text password to verify.

    Returns:
        Optional[User]: The user if credentials are valid; otherwise, None.
    """
    user = user_service.get_user_by_email(session=session, email=email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def login(session: Session, email: str, password: str) -> Token:
    """Authenticate a user and issue access and refresh tokens.

    Args:
        session (Session): Database session to use.
        email (str): User's email address.
        password (str): Plain-text password.

    Returns:
        Token: A token pair containing an access and a refresh token.

    Raises:
        HTTPException: If credentials are invalid or the user is inactive.
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
    """Register a new user in the system.

    Args:
        session (Session): Database session to use.
        payload (SignupRequest): Data required to create the user.

    Returns:
        User: The newly created user instance.

    Raises:
        HTTPException: If the email is already registered.
    """
    existing_user = user_service.get_user_by_email(
        session=session,
        email=payload.email,
    )
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email already exists.",
        )

    user_data = UserCreate.model_validate(payload)
    return user_service.create(session=session, user_data=user_data)


# ---------------------------------------------------------------------------
# Token Management
# ---------------------------------------------------------------------------


def create_access_token(user_id: UUID) -> str:
    """Generate a new signed JWT access token.

    Args:
        user_id (UUID): Identifier of the user.

    Returns:
        str: A signed access token.
    """
    return security.create_access_token(subject=user_id)


def create_refresh_token_record(session: Session, user_id: UUID) -> RefreshToken:
    """Create and persist a new refresh token record.

    Args:
        session (Session): Database session to use.
        user_id (UUID): Identifier of the associated user.

    Returns:
        RefreshToken: The newly stored refresh token record.
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
    """Validate a refresh token by checking existence, non-revocation, and expiration.

    Args:
        session (Session): Database session to use.
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
    """Revoke a refresh token so it cannot be reused.

    Args:
        session (Session): Database session to use.
        token_record (RefreshToken): The token record to revoke.
    """
    token_record.revoked = True
    token_record.revoked_at = datetime.now(timezone.utc)
    session.add(token_record)
    session.commit()


# ---------------------------------------------------------------------------
# Refresh / Logout Flow
# ---------------------------------------------------------------------------


def refresh(session: Session, refresh_token: str) -> Token:
    """Issue a new access token using a valid refresh token.

    The refresh token is validated, its last-used timestamp updated,
    and a new access token is issued.

    Args:
        session (Session): Database session to use.
        refresh_token (str): The refresh token provided by the client.

    Returns:
        Token: A token pair containing a new access token and the same
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


def logout(session: Session, refresh_token: str) -> None:
    """Logout a user by revoking their refresh token.

    Args:
        session (Session): Database session to use.
        refresh_token (str): The refresh token to revoke.

    Raises:
        HTTPException: If the refresh token is invalid.
    """
    record = validate_refresh_token(session=session, token=refresh_token)
    if not record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    revoke_refresh_token(session=session, token_record=record)
