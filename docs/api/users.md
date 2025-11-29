# 📘 Users API Documentation

This document describes the Users API of the Wallet API project. It details available endpoints, required permissions, request/response schemas, and behaviors implemented in the user service layer.

## 1. Overview

The Users API manages:

- User self-service actions (`/me`)
- Superuser-restricted user administration (CRUD)
- Password updates
- Profile updates

**Routing module:**
- `app/api/routes/users.py`

**Service layer:**
- `app/services/user_service.py`

**Authentication is implemented via:**
- JWT tokens
- Dependency: `CurrentUser`
- Superuser guard: `get_current_active_superuser`

All endpoints return Pydantic/SQLModel schemas for consistency.

## 2. Endpoints Summary

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/users/me` | GET | Get current authenticated user | User |
| `/users/me` | PATCH | Update current user profile | User |
| `/users/me/password` | PATCH | Update current user password | User |
| `/users` | GET | List all users | Superuser |
| `/users` | POST | Create a new user | Superuser |
| `/users/{user_id}` | GET | Get user by ID | Superuser |
| `/users/{user_id}` | PATCH | Update user by ID | Superuser |
| `/users/{user_id}` | DELETE | Delete user by ID | Superuser |

## 3. Schemas Used

### UserRead
Returned in almost all read/update responses.

### UserCreate
Used when a superuser creates a new user.

### UserUpdate / UserUpdateMe
Used to partially update user info.

### UpdatePassword
Used only on `/users/me/password`.

### Message
Simple response for confirmation messages.

## 4. Self-Service Endpoints (`/users/me`)

These endpoints allow the authenticated user to manage their own profile and password.

### 4.1 GET `/users/me`

**Description**

Returns the profile of the currently authenticated user.

**Response**
- `200 OK` — `UserRead`

**Logic**

Simply returns `current_user`.

### 4.2 PATCH `/users/me`

**Description**

Update the authenticated user's:
- `full_name`
- `email` (with conflict validation)

**Request Body**
- `UserUpdateMe`

**Response**
- `200 OK` — `UserRead`

**Validation**
- Email must be unique
- Only provided fields are updated

**Service Function**
- `user_service.update_me`

### 4.3 PATCH `/users/me/password`

**Description**

Allows a user to change their own password.

**Request Body**
- `UpdatePassword`

Contains:
- `current_password`
- `new_password`

**Response**
- `200 OK` — `Message(message="Password updated successfully")`

**Validation**
- Current password must match
- New password cannot be the same as the old one

**Service Function**
- `user_service.update_password`

## 5. Superuser Endpoints

These routes are protected by:
```python
dependencies=[Depends(get_current_active_superuser)]
```

Only superusers can:
- List users
- Retrieve user by ID
- Create users
- Edit users
- Delete users

### 5.1 GET `/users`

**Description**

Returns all users.

**Response**
- `200 OK` — `List[UserRead]`

**Service Function**
- `user_service.get_all`

### 5.2 POST `/users`

**Description**

Creates a new user.

**Request Body**
- `UserCreate`

Includes:
- `email`
- `full_name`
- `password`

**Response**
- `201 Created` — `UserRead`

**Validation**
- Email must be unique

**Service Function**
- `user_service.create`

### 5.3 GET `/users/{user_id}`

**Description**

Returns a specific user by UUID.

**Response**
- `200 OK` — `UserRead`

**Errors**
- `404` if the user does not exist

**Service Function**
- `user_service.get_by_id`

### 5.4 PATCH `/users/{user_id}`

**Description**

Updates any user by ID.

**Request Body**
- `UserUpdate`

Allows updating:
- `email`
- `full_name`
- `password` (converted to `hashed_password` internally)

**Response**
- `200 OK` — `UserRead`

**Validation**
- Email uniqueness enforced
- Password rehashed automatically

**Service Function**
- `user_service.update`

### 5.5 DELETE `/users/{user_id}`

**Description**

Deletes a user by ID.

**Response**
- `204 No Content`

**Errors**
- `404` if the user does not exist

**Service Function**
- `user_service.delete`

## 6. Exceptions & Error Handling

**Custom exception classes:**

| Exception | Status | Meaning |
|-----------|--------|---------|
| `UserNotFoundException` | 404 | User does not exist |
| `EmailAlreadyExistsException` | 409 | Duplicate email |
| `IncorrectPasswordException` | 400 | Wrong password |

**Additional inline exceptions:**
- Password unchanged → `400`
- User inactive (from dependency) → `400`

## 7. Service Layer Summary

The service layer handles:

✔ Business rules  
✔ Security (password hashing)  
✔ Validation (email uniqueness)  
✔ Database operations  

**Functions:**
- `get_all`
- `get_by_id`
- `get_user_by_email`
- `create`
- `update`
- `delete`
- `update_me`
- `update_password`

This separation ensures:
- Clean, testable code
- Lightweight endpoints
- Centralized logic

## 8. Example Requests

### 8.1 Get Current User

```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/users/me
```

### 8.2 Update Password

```bash
curl -X PATCH \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"current_password":"oldpass","new_password":"newpass123"}' \
  http://localhost:8000/api/v1/users/me/password
```

### 8.3 Create User (Superuser)

```bash
curl -X POST \
  -H "Authorization: Bearer <superuser_token>" \
  -H "Content-Type: application/json" \
  -d '{"email":"new@user.com","password":"Strongpass123"}' \
  http://localhost:8000/api/v1/users
```

## 9. Conclusion

The Users API provides:

- Secure self-management for users
- Full CRUD for superusers
- Consistent validation and error handling
- Clear separation between API and service logic

This module forms the foundation for authentication and user identity within the Wallet API.