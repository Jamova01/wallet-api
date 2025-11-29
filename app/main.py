from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    create_db_and_tables()
    yield
    # --- SHUTDOWN ---
    # (optional cleanup)
    pass


app = FastAPI(
    title="Wallet API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Register routers
app.include_router(api_router, prefix=settings.API_V1_STR)
