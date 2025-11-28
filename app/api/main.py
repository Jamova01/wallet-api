from fastapi import APIRouter
from app.api.routes import users

api_router = APIRouter()

# Register all routers here
api_router.include_router(users.router)
