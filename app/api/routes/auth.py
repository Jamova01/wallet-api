"""Authentication endpoints for user login, signup, and token refresh.

This module exposes the authentication-related HTTP endpoints using FastAPI
routers. Each endpoint delegates its business logic to the authentication
service layer (`auth_service`), keeping the routing layer clean and focused
on request/response handling only.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import SessionDep
from app.schemas.auth import RefreshTokenRequest, SignupRequest, Token
from app.schemas.user import UserRead
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authenticate a user and issue access + refresh tokens.

    This endpoint implements the OAuth2 Password Flow.
    The value provided in the ``username`` field is treated as the user's email.
    The credentials are validated by the authentication service, which issues
    both access and refresh tokens on success.

    Args:
        session (SessionDep):
            Database session dependency.
        form_data (OAuth2PasswordRequestForm):
            Contains ``username`` (email address) and ``password``.

    Returns:
        Token: Access and refresh JWT tokens.

    Raises:
        HTTPException:
            If the credentials are invalid or the account is inactive.
    """
    return auth_service.login(
        session=session,
        email=form_data.username,
        password=form_data.password,
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
    """Create a new user account.

    This endpoint registers a user with the provided signup data.
    Password hashing, validation, and email uniqueness checks are handled
    by the authentication service layer.

    Args:
        session (SessionDep):
            Database session dependency.
        user_in (SignupRequest):
            The signup payload containing email, password, and user information.

    Returns:
        UserRead:
            The newly created user, excluding sensitive information.

    Raises:
        HTTPException:
            If the email is already registered or validation fails.
    """
    return auth_service.signup(session=session, payload=user_in)


@router.post(
    "/refresh",
    summary="Generate a new access token using a refresh token",
    response_model=Token,
)
def refresh(
    session: SessionDep,
    refresh_token: RefreshTokenRequest,
) -> Token:
    """Issue a new access token using a valid refresh token.

    Delegates refresh-token validation and access-token generation
    to the authentication service. If the refresh token is valid,
    a new access token is issued and the existing refresh token is retained.

    Args:
        session (SessionDep):
            Database session dependency.
        refresh_token (RefreshTokenRequest):
            Request payload containing the refresh token string.

    Returns:
        Token:
            A token pair containing the new access token and the existing
            refresh token.

    Raises:
        HTTPException:
            If the refresh token is invalid, expired, or revoked.
    """
    return auth_service.refresh(
        session=session,
        refresh_token=refresh_token.refresh_token,
    )
