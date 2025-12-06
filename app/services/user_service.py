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


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------


class UserNotFoundException(HTTPException):
    """Exception raised when a user cannot be found in the database."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class EmailAlreadyExistsException(HTTPException):
    """Exception raised when attempting to register an email that already exists."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )


class IncorrectPasswordException(HTTPException):
    """Exception raised when a provided password does not match the stored hash."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )


# ---------------------------------------------------------------------------
# User Queries
# ---------------------------------------------------------------------------


def get_all(session: Session) -> List[User]:
    """
    Retrieve all users.

    Args:
        session: The active database session.

    Returns:
        List[User]: A list of all user records.
    """
    statement = select(User)
    return list(session.exec(statement).all())


def get_by_id(session: Session, user_id: UUID) -> User:
    """
    Retrieve a user by ID.

    Args:
        session: The active database session.
        user_id: The unique UUID of the user.

    Returns:
        User: The retrieved user model.

    Raises:
        UserNotFoundException: If no user exists with the given ID.
    """
    user = session.get(User, user_id)
    if not user:
        raise UserNotFoundException()
    return user


def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Retrieve a user by email address.

    Args:
        session: The active database session.
        email: Email to search for.

    Returns:
        User | None: The matched user or None if not found.
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


# ---------------------------------------------------------------------------
# User Creation & Update
# ---------------------------------------------------------------------------


def create(session: Session, user_data: UserCreate) -> User:
    """
    Create a new user.

    Args:
        session: The active database session.
        user_data: Information required to create a user.

    Returns:
        User: The newly created user instance.

    Raises:
        EmailAlreadyExistsException: If the email is already in use.
    """
    if get_user_by_email(session=session, email=user_data.email):
        raise EmailAlreadyExistsException()

    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update(session: Session, user_id: UUID, user_data: UserUpdate) -> User:
    """
    Update a user's information by ID.

    Args:
        session: The active database session.
        user_id: The user's UUID.
        user_data: Fields to update.

    Returns:
        User: The updated user instance.

    Raises:
        EmailAlreadyExistsException: If attempting to use an email already registered.
    """
    db_user = get_by_id(session=session, user_id=user_id)
    update_data = user_data.model_dump(exclude_unset=True)

    # Password update
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["hashed_password"] = get_password_hash(password)

    # Email uniqueness validation
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
    """
    Delete a user by ID.

    Args:
        session: The active database session.
        user_id: UUID of the user to delete.

    Returns:
        None
    """
    user = get_by_id(session=session, user_id=user_id)
    session.delete(user)
    session.commit()


# ---------------------------------------------------------------------------
# User Self-Service Updates
# ---------------------------------------------------------------------------


def update_me(session: Session, current_user: User, user_data: UserUpdateMe) -> User:
    """
    Update the profile of the currently authenticated user.

    Args:
        session: The active database session.
        current_user: The user who is logged in.
        user_data: Update payload for the user's own fields.

    Returns:
        User: The updated user instance.

    Raises:
        EmailAlreadyExistsException: If another user already owns the email.
    """
    update_data = user_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing = get_user_by_email(session=session, email=update_data["email"])
        if existing and existing.id != current_user.id:
            raise EmailAlreadyExistsException()

    current_user.sqlmodel_update(update_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


def update_password(
    session: Session,
    body: UpdatePassword,
    current_user: User,
) -> Message:
    """
    Update the authenticated user's password.

    Args:
        session: The active database session.
        body: Payload containing the current and new passwords.
        current_user: The authenticated user.

    Returns:
        Message: Confirmation of successful password update.

    Raises:
        IncorrectPasswordException: If the current password is invalid.
        HTTPException: If the new password is identical to the current one.
    """
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
