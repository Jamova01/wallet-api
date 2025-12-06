from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SessionDep
from app.schemas.auth import RefreshTokenRequest, SignupRequest, Token
from app.schemas.user import UserRead
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Authenticate a user and return access + refresh tokens",
    response_model=Token,
)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = auth_service.authenticate(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = auth_service.create_access_token(user_id=user.id)
    refresh_record = auth_service.create_refresh_token_record(
        session=session,
        user_id=user.id,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_record.token,
    )


@router.post(
    "/signup",
    summary="Register a new user",
    response_model=UserRead,
    status_code=201,
)
def signup(
    session: SessionDep,
    user_in: SignupRequest,
) -> UserRead:
    return auth_service.signup(session=session, payload=user_in)


@router.post(
    "/refresh",
    summary="Generate a new access token using a refresh token",
    response_model=Token,
)
def refresh(
    session: SessionDep,
    refresh_token: RefreshTokenRequest,
):
    token_record = auth_service.validate_refresh_token(
        session=session,
        token=refresh_token.refresh_token,
    )

    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    token_record.last_used_at = datetime.now(timezone.utc)
    session.add(token_record)
    session.commit()

    new_access_token = auth_service.create_access_token(user_id=token_record.user_id)

    return Token(
        access_token=new_access_token,
        refresh_token=token_record.token,
    )
