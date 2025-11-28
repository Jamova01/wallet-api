from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.api.main import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # Create database tables if they do not exist yet
    create_db_and_tables()

    yield

    # --- SHUTDOWN ---
    # Here you can add any shutdown logic if needed
    pass


app = FastAPI(
    title="Wallet API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(api_router, prefix="/api/v1")
