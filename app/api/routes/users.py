from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import CurrentUser, SessionDep, get_current_active_superuser
from app.schemas.common import Message
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserRead,
    UserUpdate,
    UserUpdateMe,
)
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    summary="Get current user",
    response_model=UserRead,
)
async def read_user_me(current_user: CurrentUser) -> UserRead:
    """
    Retrieve the profile of the currently authenticated user.

    Returns:
        UserRead: The authenticated user's information.
    """
    return current_user


@router.patch(
    "/me",
    summary="Update own user",
    response_model=UserRead,
)
async def update_user_me(
    session: SessionDep,
    user_in: UserUpdateMe,
    current_user: CurrentUser,
) -> UserRead:
    """
    Update the authenticated user's profile.

    Args:
        session: Database session dependency.
        user_in: Fields allowed for the current user to update.
        current_user: The authenticated user performing the request.

    Returns:
        UserRead: Updated user information.
    """
    return user_service.update_me(
        session=session,
        current_user=current_user,
        user_data=user_in,
    )


@router.patch(
    "/me/password",
    summary="Update own password",
    response_model=Message,
)
async def update_password_me(
    session: SessionDep,
    body: UpdatePassword,
    current_user: CurrentUser,
) -> Message:
    """
    Update the authenticated user's password.

    Args:
        session: Database session dependency.
        body: Contains the current and new password.
        current_user: The authenticated user performing the update.

    Returns:
        Message: Confirmation that the password was updated.
    """
    return user_service.update_password(
        session=session,
        body=body,
        current_user=current_user,
    )


@router.get(
    "",
    summary="Get all users",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
    response_model=List[UserRead],
)
async def read_users(session: SessionDep) -> List[UserRead]:
    """
    Retrieve all registered users.

    Accessible only to active superusers.

    Args:
        session: Database session dependency.

    Returns:
        List[UserRead]: A list of all users.
    """
    return user_service.get_all(session)


@router.post(
    "",
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserRead,
)
async def create_user(
    session: SessionDep,
    user_in: UserCreate,
) -> UserRead:
    """
    Create a new user account.

    Superuser-only operation.

    Args:
        session: Database session dependency.
        user_in: User creation payload with required fields.

    Returns:
        UserRead: The newly created user.
    """
    return user_service.create(session=session, user_data=user_in)


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserRead,
)
async def read_user(user_id: UUID, session: SessionDep) -> UserRead:
    """
    Retrieve a user by their UUID.

    Superuser-only operation.

    Args:
        user_id: Unique identifier of the user.
        session: Database session dependency.

    Returns:
        UserRead: The requested user.
    """
    return user_service.get_by_id(session=session, user_id=user_id)


@router.patch(
    "/{user_id}",
    summary="Update user",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserRead,
)
async def update_user(
    session: SessionDep,
    user_id: UUID,
    user_in: UserUpdate,
) -> UserRead:
    """
    Update a user's information by ID.

    Superuser-only operation.

    Args:
        session: Database session dependency.
        user_id: Unique identifier of the user.
        user_in: Fields to update.

    Returns:
        UserRead: Updated user data.
    """
    return user_service.update(session=session, user_id=user_id, user_data=user_in)


@router.delete(
    "/{user_id}",
    summary="Delete user",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_user(
    session: SessionDep,
    user_id: UUID,
) -> None:
    """
    Delete a user by their UUID.

    Superuser-only operation.

    Args:
        session: Database session dependency.
        user_id: The ID of the user to delete.

    Returns:
        None
    """
    user_service.delete(session=session, user_id=user_id)
