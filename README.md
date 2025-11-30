# 🏦 Wallet API

A lightweight digital wallet API built with **FastAPI** and **SQLModel**, designed as a real-world fintech mini system. Includes user management, accounts with balances, transactions, and a double-entry ledger foundation.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

---

## ✨ Features

- 👤 **User registration & authentication**
- 💳 **Account creation and balance tracking**
- 💸 **Money transfers & transaction records**
- 📒 **Double-entry ledger model**
- 🏗️ **Clean, extensible architecture** for future modules (fraud engine, Kafka events, etc.)

---

## 🚀 Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern, fast web framework for building APIs |
| **SQLModel** | SQL databases in Python with type hints |
| **PostgreSQL** | Robust relational database |
| **Docker** | Containerization for easy deployment |

---

## 📋 Prerequisites

Before running the project, ensure you have:

- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL** (if running locally without Docker)

---

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/Jamova01/wallet-api.git
cd wallet-api
```

### 2. Install uv (recommended)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### 3. Install dependencies
```bash
# uv automatically creates a virtual environment and installs all dependencies
uv sync
```

### 4. Run the API
```bash
# Activate the virtual environment to use project-specific dependencies 
source .venv/bin/activate

# Start the FastAPI application in development mode
# This will run the server at http://127.0.0.1:8000
fastapi dev app/main.py
```
### 5. Set up environment variables

Create a `.env` file in the root directory:
```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1

# First superuser
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=supersecurepassword
```

## 👨‍💻 Author

**Your Name**

- GitHub: [@Jamova01](https://github.com/Jamova01)
- Email: jorgemova01@gmail.com

**⭐ If you find this project useful, please consider giving it a star!**
