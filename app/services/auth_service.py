from fastapi import HTTPException
from sqlmodel import Session

from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import SignupRequest
from app.schemas.user import UserCreate
from app.services import user_service


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """
    Validate user credentials and return the user if authentication succeeds.
    """
    user = user_service.get_user_by_email(session=session, email=email)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def signup(*, session: Session, payload: SignupRequest) -> User:
    """
    Register a new user without authentication.
    """
    existing_user = user_service.get_user_by_email(session=session, email=payload.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user_data = UserCreate.model_validate(payload)
    new_user = user_service.create(session=session, user=user_data)

    return new_user
