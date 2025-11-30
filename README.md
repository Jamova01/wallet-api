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

<!-- 


---

## 🐳 Running with Docker

### Build and run containers
```bash
docker-compose up --build
```

The API will be available at: **http://localhost:8000**

### API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🏃 Running Locally (Without Docker)

### 1. Start PostgreSQL

Ensure PostgreSQL is running and create a database:
```sql
CREATE DATABASE wallet_db;
```

### 2. Run the application
```bash
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

---

## 📂 Project Structure
```
wallet-api/
├── app/
│   ├── api/                # API routes
│   │   └── v1/
│   │       ├── users.py
│   │       ├── accounts.py
│   │       └── transactions.py
│   ├── core/               # Core configurations
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/             # SQLModel database models
│   │   ├── user.py
│   │   ├── account.py
│   │   └── transaction.py
│   ├── schemas/            # Pydantic schemas
│   └── main.py             # Application entry point
├── tests/                  # Unit and integration tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔐 Authentication

The API uses **JWT (JSON Web Tokens)** for authentication.

### Register a new user
```bash
POST /api/v1/users/register
```

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe"
}
```

### Login
```bash
POST /api/v1/auth/login
```

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## 💰 API Endpoints

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/users/register` | Register a new user |
| GET | `/api/v1/users/me` | Get current user info |

### Accounts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/accounts` | Create a new account |
| GET | `/api/v1/accounts` | List user accounts |
| GET | `/api/v1/accounts/{id}` | Get account details |

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transactions/transfer` | Transfer money between accounts |
| GET | `/api/v1/transactions` | List transactions |
| GET | `/api/v1/transactions/{id}` | Get transaction details |

---

## 🧪 Testing

Run tests with:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=app tests/
```

---

## 🗺️ Roadmap

Future enhancements planned:

- [ ] Fraud detection engine
- [ ] Kafka event streaming integration
- [ ] Multi-currency support
- [ ] Transaction categorization
- [ ] Scheduled payments
- [ ] Notifications system
- [ ] Admin dashboard

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---


---

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- SQLModel for seamless database integration
- The open-source community

---

 -->