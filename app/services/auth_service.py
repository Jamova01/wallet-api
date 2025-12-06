from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlmodel import Session, select

from app.core import security
from app.core.security import verify_password
from app.models.user import User
from app.models.token import RefreshToken
from app.schemas.auth import SignupRequest
from app.schemas.user import UserCreate
from app.services import user_service
from app.core.config import settings


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    user = user_service.get_user_by_email(session=session, email=email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def signup(*, session: Session, payload: SignupRequest) -> User:
    existing_user = user_service.get_user_by_email(session=session, email=payload.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user_data = UserCreate.model_validate(payload)
    return user_service.create(session=session, user_data=user_data)


def create_access_token(*, user_id: int) -> str:
    return security.create_access_token(subject=user_id)


def create_refresh_token_record(
    *,
    session: Session,
    user_id: int,
) -> RefreshToken:
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


def validate_refresh_token(
    *,
    session: Session,
    token: str,
) -> RefreshToken | None:
    token_record = session.exec(
        select(RefreshToken).where(RefreshToken.token == token)
    ).first()

    if not token_record:
        return None

    if token_record.revoked:
        return None

    if token_record.expires_at.tzinfo is None:
        token_record.expires_at = token_record.expires_at.replace(tzinfo=timezone.utc)

    if token_record.expires_at < datetime.now(timezone.utc):
        return None

    return token_record


def revoke_refresh_token(
    *,
    session: Session,
    token_record: RefreshToken,
) -> None:
    token_record.revoked = True
    session.add(token_record)
    session.commit()
