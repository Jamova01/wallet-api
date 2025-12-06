"""Authentication endpoints for user login, signup, token refresh, and logout.

This module exposes the authentication-related HTTP endpoints using FastAPI
routers. Each endpoint delegates its business logic to the authentication
service layer (`auth_service`), keeping the routing layer focused on handling
request/response serialization and HTTP routing.
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
    """Authenticate a user and issue access and refresh tokens.

    Implements the OAuth2 Password Flow where the ``username`` field is treated
    as the user's email. Credentials are validated by the authentication service,
    which issues both access and refresh tokens upon successful authentication.

    Args:
        session (SessionDep): Database session dependency.
        form_data (OAuth2PasswordRequestForm): Form data containing
            ``username`` (email) and ``password``.

    Returns:
        Token: A token pair containing both access and refresh tokens.

    Raises:
        HTTPException: If the credentials are invalid or the user is inactive.
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
    """Register a new user account.

    This endpoint processes a signup request and delegates validation,
    hashing, and email uniqueness checks to the authentication service.

    Args:
        session (SessionDep): Database session dependency.
        user_in (SignupRequest): Signup payload containing user information.

    Returns:
        UserRead: The newly created user object without sensitive fields.

    Raises:
        HTTPException: If the email is already registered or validation fails.
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

    Delegates validation and token rotation logic to the authentication service.
    If the refresh token is valid, a new access token is issued while retaining
    the existing refresh token.

    Args:
        session (SessionDep): Database session dependency.
        refresh_token (RefreshTokenRequest): Payload containing the refresh token.

    Returns:
        Token: A token pair containing the new access token and the existing
            refresh token.

    Raises:
        HTTPException: If the refresh token is invalid, expired, or revoked.
    """
    return auth_service.refresh(
        session=session,
        refresh_token=refresh_token.refresh_token,
    )


@router.post(
    "/logout",
    summary="Revoke a refresh token and log out the user",
    response_model=None,
    status_code=204,
)
def logout(
    session: SessionDep,
    refresh_token: RefreshTokenRequest,
) -> None:
    """Log out a user by revoking their refresh token.

    This endpoint invalidates the specified refresh token, preventing further
    use for token renewal. Logout does not return content.

    Args:
        session (SessionDep): Database session dependency.
        refresh_token (RefreshTokenRequest): Payload containing the refresh token.

    Raises:
        HTTPException: If the refresh token is invalid.
    """
    return auth_service.logout(
        session=session,
        refresh_token=refresh_token.refresh_token,
    )
