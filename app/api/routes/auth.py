from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SessionDep
from app.core import security
from app.core.config import settings
from app.schemas.auth import SignupRequest, Token
from app.schemas.user import UserRead
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    summary="Authenticate a user and return an access token",
    response_model=Token,
)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    OAuth2-compatible login endpoint.

    - Accepts username/email and password
    - Returns a signed JWT access token
    """
    user = auth_service.authenticate(
        session=session,
        email=form_data.username,
        password=form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Inactive user",
        )

    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=expires,
    )

    return Token(access_token=access_token)


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
    """
    Public user registration endpoint.
    Creates a new account with email and password.
    """
    return auth_service.signup(session=session, payload=user_in)
