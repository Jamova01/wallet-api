from typing import List
from uuid import UUID
from fastapi import APIRouter, status, Response
from app.api.dependencies import SessionDep
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "",
    summary="Get all users",
    status_code=status.HTTP_200_OK,
    response_model=List[UserRead],
)
async def read_users(session: SessionDep) -> List[UserRead]:
    return user_service.get_all(session)


@router.post(
    "",
    summary="Create a new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
)
async def create_user(user: UserCreate, session: SessionDep):
    return user_service.create(session, user)


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
)
async def read_user(user_id: UUID, session: SessionDep) -> UserRead:
    return user_service.get_by_id(session, user_id)


@router.put(
    "/{user_id}",
    summary="Update user completely",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
)
async def update_user(user_id: UUID, user: UserUpdate, session: SessionDep) -> UserRead:
    return user_service.update(session, user_id, user)


@router.delete(
    "/{user_id}",
    summary="Delete user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: UUID, session: SessionDep) -> None:
    user_service.delete(session, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
