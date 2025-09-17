import logging

from fastapi import APIRouter, FastAPI

from app.auth.router import auth_router
from app.config import settings

logging.basicConfig(level=logging.INFO)

api_router = APIRouter()
api_router.include_router(auth_router)


app = FastAPI(
    title="Nitty",
    description="Professional Communities but fun",
    version="0.1.0",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
