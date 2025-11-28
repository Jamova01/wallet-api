from typing import List
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate


def get_all(session: Session) -> List[UserRead]:
    return session.exec(select(User)).all()


def get_by_id(session: Session, user_id: UUID) -> UserRead:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )
    return user


def create(session: Session, user: UserCreate) -> UserRead:
    existing = session.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    hashed = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update(session: Session, user_id: UUID, user: UserUpdate) -> UserRead:
    db_user = get_by_id(session, user_id)

    update_data = user.model_dump(exclude_unset=True)

    if "password" in update_data:
        new_password = update_data.pop("password")
        db_user.hashed_password = get_password_hash(new_password)

    db_user.sqlmodel_update(update_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete(session: Session, user_id: UUID) -> None:
    user = get_by_id(session, user_id)
    session.delete(user)
    session.commit()
