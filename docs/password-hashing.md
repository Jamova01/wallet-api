# 🔐 Password Hashing & Authentication Security Guide

## 1. Overview

This document explains how password hashing is implemented in the project, why it is done this way, and how other developers should work with authentication-related code.

It applies to **all subsystems interacting with user credentials**.

### The goal is to ensure:

- Strong, modern password hashing (Argon2id)
- Zero plaintext password storage
- Safe verification of credentials
- Compatibility with future hashing algorithm upgrades
- Predictable and auditable authentication logic

---

## 2. Hashing Algorithm: Argon2id (via pwdlib)

### Why Argon2id?

**Argon2id** is currently considered one of the most secure password hashing algorithms. It is:

- **Memory-hard** → resistant to GPU/ASIC brute-force attacks
- Recommended by modern cryptographic standards (OWASP, PHC)
- Deployed by major authentication systems

The project uses `pwdlib[argon2]` to manage hashing and verification:
```bash
pip install "pwdlib[argon2]"
```

### Library

`pwdlib` provides:

- Safe defaults (`PasswordHash.recommended()`)
- Automatic generation of salts
- Automatic versioning of hashing parameters
- A unified API for verifying hashes, including support for legacy formats (Django, Flask, passlib-based systems, etc.)

---

## 3. Implementation

The password hashing logic lives in:

**`app/core/security.py`**
```python
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
```

### Key behaviors

**Automatic salts:**
- Every password is hashed using a unique, randomly generated salt

**Non-reversible:**
- No plaintext password can be recovered from a hash

**Consistent verification:**
- `verify_password()` automatically detects the hashing scheme and parameters for each stored hash

**Upgrade-friendly:**
- If parameters change, old hashes still verify, and new ones are automatically generated with stronger settings

---

## 4. Password Hashing Process (Step by Step)

### 1. User provides a password

**Example:** `"mySecurePass123"`

### 2. System hashes it

Using:
```python
hashed = get_password_hash("mySecurePass123")
```

Produces something like:
```
$argon2id$v=19$m=65536,t=2,p=4$8A94...$Vn93...
```

A hash contains:

- **algorithm** (argon2id)
- **version**
- **memory cost**
- **time cost**
- **parallelism**
- **salt**
- **hash**

### 3. Hash is stored in the database

**Only the hash is saved** → never the plaintext password.

### 4. User logs in

The system verifies the password using:
```python
verify_password(plain, stored_hash)
```

**Verification:**

- Recreates the hashing flow
- Uses the salt inside the stored hash
- Compares hashes in a constant-time operation (prevents timing attacks)

---

## 5. Why Password Hashing Is Necessary

### If the database is breached

The attacker gets only hashes, not real passwords.

Since many users reuse passwords across multiple sites, strong hashing prevents:

- Credential stuffing
- Account takeover
- Lateral attacks into other systems

### Security Benefits

| Threat | Protection Provided |
|--------|---------------------|
| Raw password leakage | Fully protected (hash is non-reversible) |
| Rainbow table attacks | Prevented by per-user salts |
| Offline brute force | Greatly slowed by Argon2id memory hardness |
| GPU/ASIC cracking | Argon2id is resistant |
| Timing attacks | pwdlib uses constant-time verification |

---

## 6. Future-Proofing and Migration

`pwdlib` supports:

Reading/verifying passwords created by:

- Django
- Flask security plugins
- passlib formats
- Other systems

### This means:

#### Possible use case

If you migrate users from **Django → FastAPI**:

- Django-stored PBKDF2 passwords remain valid
- New passwords are hashed with Argon2id
- Users can log in from both systems simultaneously during migration

This enables smooth cross-framework authentication across microservices or monolith transitions.

---

## 7. Password Rules & Recommendations

### Minimum password length

The project enforces:
```python
password: str = Field(min_length=8)
```

**Recommended minimum:**

- 8 characters (required)
- Ideally 12+ characters for strong passwords

### Avoid plaintext handling

- ❌ Never log user passwords (even in dev)
- ❌ Never send passwords back in API responses
- ❌ Never store temporary passwords unencrypted

### Optional future enhancements

- Rate limiting login attempts
- Multi-factor authentication
- Password breach detection using k-anonymity (HaveIBeenPwned)
- Sessions revocation policies

---

## 8. Developer Notes: How to Implement Safe Authentication

### To hash a password
```python
hashed = get_password_hash("my-password")
```

### To verify a login
```python
verify_password(plain_password, stored_hash)
```

### To update a password

Always hash again:
```python
new_hashed = get_password_hash(new_password)
```

### NEVER do the following

- ❌ Store plaintext passwords
- ❌ Compare plaintext with plaintext
- ❌ Reuse salts manually
- ❌ Roll your own crypto
- ❌ Return hashed passwords in API responses
- ❌ Pass passwords via GET parameters

---

## 9. Security Checklist

Every pull request touching authentication must ensure:

- ✅ Passwords are hashed BEFORE storing
- ✅ Hashes are never returned by the API
- ✅ `verify_password` is used consistently
- ✅ No plaintext passwords appear in logs
- ✅ No accidental exposure in exception messages
- ✅ No manual hashing parameters (we use recommended defaults)

---

## 10. Summary

This project uses **Argon2id** via `pwdlib[argon2]`, following modern cryptographic best practices. Password hashing is centralized in `app/core/security.py` using strong defaults, safe verification practices, and future-proof extendability.

By following this guide, developers can confidently work on authentication-related features without weakening the security model.

---

**🔒 Security is not a feature—it's a foundation.**