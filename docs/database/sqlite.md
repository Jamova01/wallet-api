# 📘 Database Setup – SQLite + SQLModel + FastAPI

This document explains how the database of the **Wallet API project** is configured. It covers the engine setup, session handling, automatic table creation, and how to work with the database inside FastAPI.

---

## 1. 📦 Technologies Used

- **SQLModel** (models + ORM + Pydantic-style validation)
- **SQLite** (lightweight database for local development)
- **FastAPI**
- **SQLAlchemy engine**
- **Pydantic Settings** (environment variables)

> **Note:** Ideal setup for local development. Switching to PostgreSQL later requires minimal changes.

---

## 2. 📁 Relevant Project Structure
```
app/
├── core/
│   ├── config.py         ← Environment variables (incl. superuser)
│   ├── database.py       ← DB engine + session + table creation
│   └── superuser.py      ← Logic to create first superuser
├── main.py               ← FastAPI instance + lifespan startup process
└── models/               ← SQLModel models

```

---

## 3. ⚙️ Database Configuration (`database.py`)

**File:** `app/core/database.py`
```python
from sqlmodel import Session, SQLModel, create_engine

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_sync_session() -> Session:
    return Session(engine)
```

### 3.1 Engine Configuration

```python
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
```

- Uses a local SQLite file
- Allows multithread access (`check_same_thread=False`)
- Zero external dependencies

### 3.2 Automatic Table Creation

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```
- Executed on startup to ensure all SQLModel tables exist.

### 3.3 Session Handling

Two session providers exist:

| Function | Usage |
|----------|-------|
| `get_session()` | Async dependencies inside routes |
| `get_sync_session()` | Synchronous logic executed at startup, e.g., superuser creation |

---

## 4. 🔐 Superuser Auto-Creation

A key part of the system initialization is the automatic creation of the first superuser, defined via environment variables.

### 4.1 Settings Configuration (`config.py`)

```python
FIRST_SUPERUSER: EmailStr
FIRST_SUPERUSER_PASSWORD: str
```

These values are read from `.env`.

### 4.2 Superuser Logic (`superuser.py`)

```python
def create_first_superuser(session: Session):
    # Checks if a superuser exists; if not, creates one
```

### 4.3 When is the Superuser Created?

Inside `main.py`, during the lifespan startup event:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    session = get_sync_session()
    create_first_superuser(session)
    session.close()

    yield
```

This ensures:
- Tables exist
- Superuser is created only once
- Works synchronously before the app starts serving requests

## 5. 🚀 Integration with FastAPI (`main.py`)

**File:** `app/main.py`
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import create_db_and_tables, get_sync_session
from app.core.superuser import create_first_superuser
```

### 5.1 Lifespan Function
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    session = get_sync_session()
    create_first_superuser(session)
    session.close()

    yield

    pass
```

Startup sequence:

- Create database and tables

- Open a synchronous session

- Create first superuser

- Close session

- Start API

## 6. ▶️ Using the Database in Endpoints

**Example:**
```python
@router.get("/users")
def read_users(session: SessionDep):
    return session.exec(select(User)).all()
```

Dependency injection is defined like:
```python
SessionDep = Annotated[Session, Depends(get_session)]
```

- Each request receives its own session

---

## 7. 📄 Where the Database is Stored

SQLite automatically creates the file:
```
database.db
```

You can inspect it using:

- **DB Browser for SQLite**
- **DBeaver**
- **CLI:** `sqlite3 database.db`

---

## 8. 🔄 Migrating to PostgreSQL (Future Phase)

Your current structure is fully compatible with PostgreSQL.

To switch, you would only update:
```python
sqlite_url = "postgresql+psycopg://user:password@host:5432/dbname"
engine = create_engine(sqlite_url, echo=True)
```

And add a migration tool like **Alembic**.

---

## 9. ✔️ Advantages of This Setup

- Simple and ideal for development
- Automatic table & superuser creation
- Clean separation of concerns
- Ready for future database scaling

---

## 10. 📌 Conclusion

With this setup you get:

- ✅ SQLite database configured with SQLModel
- ✅ Automatic creation of tables
- ✅ Automatic creation of the initial superuser
- ✅ FastAPI lifespan handling for startup tasks
- ✅ Ready-to-scale architecture
