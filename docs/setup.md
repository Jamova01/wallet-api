# Setup Guide: FastAPI Development Environment

This guide provides the necessary steps to configure a complete development environment for working with FastAPI, following industry best practices.

## Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) installed (fast package manager for Python)
- Git installed

## Initial Setup

### 1. Create project directory

```bash
mkdir wallet-api
cd wallet-api
```

### 2. Initialize Git repository

```bash
git init
```

This creates a local repository for version control of your code.

### 3. Initialize project with uv

```bash
uv init
```

This command automatically generates:

- **`pyproject.toml`**: Project configuration and dependency management file
- Basic project structure

### 4. Create and activate virtual environment

The virtual environment isolates project dependencies from the global system.

```bash
# Create virtual environment
uv venv

# Activate on Linux/macOS
source .venv/bin/activate

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate on Windows (CMD)
.venv\Scripts\activate.bat
```

> **Note**: You'll see the environment name `(.venv)` in your terminal when it's active.

### 5. Install main dependencies

```bash
# Install FastAPI with standard dependencies (includes uvicorn, pydantic, etc.)
uv add "fastapi[standard]"

# Install SQLModel (ORM that combines SQLAlchemy + Pydantic)
uv add sqlmodel
```

### 6. Create project folder structure

```bash
# Create base structure with subfolders
mkdir -p app/{api,core,models,schemas,services}
mkdir -p docs tests

# Create __init__.py files in each module
touch app/__init__.py \
      app/api/__init__.py \
      app/core/__init__.py \
      app/models/__init__.py \
      app/schemas/__init__.py \
      app/services/__init__.py

# Create main application file
touch app/main.py

# Create documentation
touch README.md docs/setup.md
```

### 7. Configure .gitignore file

Create a `.gitignore` file to avoid committing unnecessary files to the repository:

```bash
cat > .gitignore << 'EOF'
# Virtual environment
.venv/
venv/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Databases
*.db
*.sqlite3

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# Operating system
.DS_Store
Thumbs.db
EOF
```

## Project Structure

The project follows the **layered architecture** pattern, where each folder has a specific responsibility:

```
wallet-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   │
│   ├── api/                    # 🔗 Endpoints and routers layer
│   │   ├── __init__.py
│   │   ├── routes/             # Routers organized by domain
│   │   └── dependencies.py     # Shared FastAPI dependencies
│   │
│   ├── core/                   # ⚙️ Core configuration
│   │   ├── __init__.py
│   │   ├── config.py           # Settings and environment variables
│   │   ├── database.py         # Database connection
│   │   └── security.py         # Authentication and authorization
│   │
│   ├── models/                 # 💾 Database models (SQLModel)
│   │   ├── __init__.py
│   │   └── user.py             # Example: user model
│   │
│   ├── schemas/                # 📋 Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   └── user.py             # Example: user schemas
│   │
│   └── services/               # 💼 Business logic
│       ├── __init__.py
│       └── user_service.py     # Example: user service
│
├── tests/                      # 🧪 Unit and integration tests
│   ├── __init__.py
│   └── test_api/
│
├── docs/                       # 📚 Project documentation
│   └── setup.md
│
├── .venv/                      # Virtual environment (do not version)
├── .gitignore                  # Files ignored by Git
├── pyproject.toml              # Configuration and dependencies
├── uv.lock                     # Dependencies lock file
└── README.md                   # Main documentation
```

## Layer Responsibilities

| Layer | Purpose | Examples |
|-------|---------|----------|
| **api/** | Defines HTTP endpoints and input validation | `@app.get("/users")`, routers, middleware |
| **core/** | Global configuration and cross-cutting utilities | Settings, DB connection, JWT, CORS |
| **models/** | Represents database tables | SQLModel classes with fields and relationships |
| **schemas/** | Defines data structures for API | Request/response bodies, validations |
| **services/** | Contains business logic | CRUD operations, calculations, business rules |

## Next Steps

1. **Configure the database** in `app/core/database.py`
2. **Create your first model** in `app/models/`
3. **Define schemas** in `app/schemas/`
4. **Implement services** in `app/services/`
5. **Create endpoints** in `app/api/`
6. **Run the application**:
   ```bash
   fastapi dev app/main.py
   ```

## Useful Commands

```bash
# Install a new dependency
uv add package-name

# Install development dependencies
uv add --dev pytest pytest-cov

# Update dependencies
uv sync

# Run the application in development mode
fastapi dev app/main.py

# Run the application in production
fastapi run app/main.py

# View interactive documentation
# http://127.0.0.1:8000/docs (Swagger UI)
# http://127.0.0.1:8000/redoc (ReDoc)
```

## Additional Resources

- [Official FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [uv Guide](https://github.com/astral-sh/uv)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)

---

**Found an error or have suggestions?** Contribute to improve this documentation.