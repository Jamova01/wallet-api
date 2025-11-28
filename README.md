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

### 2. Install uv (if not already installed)
```bash
# Use curl to download the script and execute it with sh:
curl -LsSf https://astral.sh/uv/install.sh | sh

# If your system doesn't have curl, you can use wget:
wget -qO- https://astral.sh/uv/install.sh | sh

# Request a specific version by including it in the URL:
curl -LsSf https://astral.sh/uv/0.9.13/install.sh | sh
```
### 3. Install dependencies
```bash
# uv automatically creates a virtual environment and installs all dependencies
uv sync
```

### 4. Activate the virtual environment (optional)
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

> **💡 Tip:** With uv, you can run commands directly without activating the environment:
> ```bash
> uv run uvicorn app.main:app --reload
> ```
