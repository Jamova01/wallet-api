from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.common import Message
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserUpdate,
    UserUpdateMe,
)


class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class EmailAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )


class IncorrectPasswordException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )


def get_all(session: Session) -> List[User]:
    """Retrieve all users."""
    statement = select(User)
    return list(session.exec(statement).all())


def get_by_id(session: Session, user_id: UUID) -> User:
    """Retrieve a user by ID or raise 404."""
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundException()
    return user


def get_user_by_email(session: Session, email: str) -> User | None:
    """Retrieve a user by email."""
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create(session: Session, user: UserCreate) -> User:
    """Create a new user."""
    if get_user_by_email(session=session, email=user.email):
        raise EmailAlreadyExistsException()

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update(session: Session, user_id: UUID, user: UserUpdate) -> User:
    """Update a user's information by ID."""
    db_user = get_by_id(session=session, user_id=user_id)
    update_data = user.model_dump(exclude_unset=True)

    if "password" in update_data:
        password = update_data.pop("password")
        update_data["hashed_password"] = get_password_hash(password)

    if "email" in update_data:
        existing = get_user_by_email(session=session, email=update_data["email"])
        if existing and existing.id != user_id:
            raise EmailAlreadyExistsException()

    db_user.sqlmodel_update(update_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete(session: Session, user_id: UUID) -> None:
    """Delete a user by ID."""
    user = get_by_id(session=session, user_id=user_id)
    session.delete(user)
    session.commit()


def update_me(session: Session, current_user: User, user: UserUpdateMe) -> User:
    """Update the currently authenticated user's profile."""
    user_data = user.model_dump(exclude_unset=True)
    if "email" in user_data:
        existing = get_user_by_email(session=session, email=user_data["email"])
        if existing and existing.id != current_user.id:
            raise EmailAlreadyExistsException()

    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def update_password(
    session: Session, body: UpdatePassword, current_user: User
) -> Message:
    """Update the currently authenticated user's password."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise IncorrectPasswordException()

    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current one",
        )

    current_user.hashed_password = get_password_hash(body.new_password)
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")
