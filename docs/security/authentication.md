# 🔐 Authentication Guide

This document explains how authentication is implemented in the **Wallet API**, following FastAPI's **OAuth2 Password Flow** with **JWT access tokens**.

---

## 📋 Implementation Roadmap

### Nivel 1 - Autenticación mínima funcional para wallet

| Feature | Status |
|---------|--------|
| Login (email + password) | ✔️ |
| Signup | ✔️ |
| Access Token (15–30 min) | ✔️ |
| Refresh Token (7–30 días) | ✔️ |
| Refresh endpoint | ✔️ |
| Logout (revocar refresh token) | ✔️ |
| Hashing fuerte (bcrypt + pepper) | ✔️ |
| Rate limit básico (5 intentos / 10 min) | ✔️ |

---

## 📦 1. Install Dependencies

### PyJWT
Used for generating and verifying JWT tokens.

```bash
uv add pyjwt
```

### pwdlib with Argon2
Used for secure password hashing.

```bash
uv add "pwdlib[argon2]"
```

---

## 🔑 2. Password Hashing

To protect stored credentials, user passwords are **never saved directly**.
Instead, they are hashed using **Argon2** via `pwdlib`.

### Why hashing matters
- If the database is stolen, attackers cannot read plaintext passwords
- Users commonly reuse passwords across services—hashing prevents direct leakage

### Implementation (`app/core/security.py`)

```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
```

---

## 🔐 3. JWT Token Generation

Authentication uses **JWT access tokens** signed with a secret key.

### Generate a secure key:

```bash
openssl rand -hex 32
```

**Example output (do NOT use this key):**
```
09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
```

### Add it to your `.env`:

```env
SECRET_KEY=your_generated_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## ⚙️ 4. Settings Configuration (`app/core/config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

settings = Settings()
```

---

## 🧩 5. Token Schemas (`app/schemas/auth.py`)

```python
from sqlmodel import SQLModel

class Token(SQLModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None
    type: str | None = None  # "access" or "refresh"
```

---

## 🛠️ 6. Creating Access & Refresh Tokens (`app/core/security.py`)

```python
from datetime import datetime, timezone, timedelta
import jwt
from app.core.config import settings

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

def create_refresh_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
```

---

## 🔍 7. Authenticating a User (`app/services/auth_service.py`)

```python
from sqlmodel import Session
from app.core.security import verify_password
from app.services.user_service import get_user_by_email
from app.models.user import User

def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user
```

---

## 🚪 8. Authentication Routes (`app/api/routes/auth.py`)

### Login Endpoint

Implements the **OAuth2 Password Flow** (`/auth/access-token`).

```python
@router.post("/access-token", summary="Get access token")
def get_access_token(
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
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    refresh_token_expires = timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
    )
    refresh_token = security.create_refresh_token(
        user.id,
        expires_delta=refresh_token_expires,
    )
    
    # Store refresh token in database
    auth_service.store_refresh_token(
        session=session,
        user_id=user.id,
        token=refresh_token
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )
```

### Signup Endpoint

```python
@router.post("/signup", summary="Register new user")
def signup(
    session: SessionDep,
    user_in: UserCreate,
) -> User:
    # Check if user already exists
    existing_user = get_user_by_email(session=session, email=user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with hashed password
    hashed_password = security.get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return db_user
```

### Refresh Token Endpoint

```python
@router.post("/refresh", summary="Refresh access token")
def refresh_token(
    session: SessionDep,
    refresh_token: str,
) -> Token:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
        
        # Verify token type
        if token_data.type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        # Verify token is not revoked
        if not auth_service.verify_refresh_token(session, refresh_token):
            raise HTTPException(status_code=401, detail="Token has been revoked")
            
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user = session.get(User, token_data.sub)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id,
        expires_delta=access_token_expires,
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )
```

### Logout Endpoint

```python
@router.post("/logout", summary="Logout and revoke refresh token")
def logout(
    session: SessionDep,
    current_user: CurrentUser,
    refresh_token: str,
) -> dict:
    # Revoke the refresh token
    auth_service.revoke_refresh_token(
        session=session,
        user_id=current_user.id,
        token=refresh_token
    )
    
    return {"message": "Successfully logged out"}
```

---

## 🔒 9. Protected Routes & Dependencies (`app/api/dependencies.py`)

### OAuth2 Bearer scheme

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/access-token")
```

### Extracting and validating the current user

```python
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        token_data = TokenPayload(**payload)
        
        # Verify token type
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
            
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
```

### Reusable dependency

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

### Checking superuser privileges

```python
def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return current_user
```

---

## 🛡️ 10. Rate Limiting

Implement basic rate limiting to prevent brute force attacks (5 intentos / 10 min).

### Using slowapi

```bash
uv add slowapi
```

### Implementation

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/access-token")
@limiter.limit("5/10minutes")
def get_access_token(
    request: Request,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # ... authentication logic
```

---

## 🏁 Summary

| Feature | Status |
|---------|--------|
| Password hashing (Argon2) | ✅ Implemented |
| JWT access token creation | ✅ Implemented |
| JWT refresh token creation | ✅ Implemented |
| OAuth2 Password Flow | ✅ Implemented |
| Login endpoint | ✅ `/auth/access-token` |
| Signup endpoint | ✅ `/auth/signup` |
| Refresh endpoint | ✅ `/auth/refresh` |
| Logout endpoint | ✅ `/auth/logout` |
| Protected dependencies | ✅ `CurrentUser`, `get_current_active_superuser` |
| Environment-driven config | ✅ `pydantic-settings` |
| Rate limiting | ✅ 5 attempts / 10 minutes |

---

## 🔐 Security Best Practices

- ✅ Never commit your `SECRET_KEY` to version control
- ✅ Use environment variables for sensitive configuration
- ✅ Always hash passwords before storing them (using Argon2 or bcrypt)
- ✅ Set appropriate token expiration times (15-30 min for access, 7-30 days for refresh)
- ✅ Validate tokens on every protected endpoint
- ✅ Implement rate limiting on authentication endpoints (5 attempts / 10 min)
- ✅ Store refresh tokens securely and implement revocation
- ✅ Use separate token types for access and refresh tokens
- ✅ Always verify token type before processing
- ✅ Implement logout functionality to revoke refresh tokens