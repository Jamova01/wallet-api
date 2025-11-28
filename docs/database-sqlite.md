# 📘 Database Setup – SQLite + SQLModel + FastAPI

This document explains how the database of the **Wallet API project** is configured. It covers the engine setup, session handling, automatic table creation, and how to work with the database inside FastAPI.

---

## 1. 📦 Technologies Used

- **SQLModel** (models + ORM + Pydantic-style validation)
- **SQLite** (lightweight database for local development)
- **FastAPI**
- **SQLAlchemy engine**

> **Note:** This setup is ideal for development. You can later switch to PostgreSQL with minimal changes.

---

## 2. 📁 Relevant Project Structure
```
app/
├── core/
│   └── database.py     ← DB engine + session + table creation
├── main.py             ← FastAPI instance with lifespan hook
└── models/             ← SQLModel models
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
```

### 3.1 Engine Configuration
```python
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
```

- Uses a local SQLite file
- `check_same_thread=False` allows the database to be accessed across threads (needed for FastAPI)
- No external DB server is required

### 3.2 Automatic Table Creation
```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

- This creates all SQLModel-defined tables if they do not already exist
- This function is executed automatically on application startup (see lifespan section)

### 3.3 Session Handling
```python
def get_session():
    with Session(engine) as session:
        yield session
```

- Uses a generator with `yield`, enabling FastAPI to manage the session lifecycle
- It is injected into endpoints using FastAPI dependencies:
```python
def read_users(session: SessionDep):
    session.exec(...)
```

---

## 4. 🚀 Integration with FastAPI (`main.py`)

**File:** `app/main.py`
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import create_db_and_tables
from app.api.main import api_router
```

### 4.1 Lifespan Function
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
```

FastAPI runs this in two phases:

**Startup:**
- Ensures all database tables exist
- Ideal for initializing system resources

**Shutdown:**
- You may place cleanup logic here if needed

### Registering the Lifespan
```python
app = FastAPI(lifespan=lifespan)
```

> **Important:** Because of this mechanism, you do not need to run migration scripts for SQLite in development.

---

## 5. ▶️ Using the Database in Endpoints

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

## 6. 📄 Where the Database is Stored

SQLite automatically creates the file:
```
database.db
```

You can inspect it using:

- **DB Browser for SQLite**
- **DBeaver**
- **CLI:** `sqlite3 database.db`

---

## 7. 🔄 Migrating to PostgreSQL (Future Phase)

Your current structure is fully compatible with PostgreSQL.

To switch, you would only update:
```python
sqlite_url = "postgresql+psycopg://user:password@host:5432/dbname"
engine = create_engine(sqlite_url, echo=True)
```

And add a migration tool like **Alembic**.

---

## 8. ✔️ Advantages of This Setup

- Simple and perfect for development
- Automatic table creation on startup
- Easy to migrate to production databases later
- Clean integration with FastAPI's lifespan and dependency injection

---

## 9. 📌 Conclusion

With this setup you get:

- ✅ A fully configured SQLModel database engine
- ✅ Automatic table creation at startup
- ✅ Session lifecycle management through FastAPI
- ✅ A foundation ready to scale to PostgreSQL
