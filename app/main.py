from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.main import api_router
from app.core.config import settings
from app.core.database import create_db_and_tables, get_sync_session
from app.core.superuser import create_first_superuser


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    session = get_sync_session()
    create_first_superuser(session)
    session.close()

    yield

    pass


app = FastAPI(
    title="Wallet API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(api_router, prefix=settings.API_V1_STR)
