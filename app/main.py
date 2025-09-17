import logging

from fastapi import APIRouter, FastAPI

from app.auth.router import auth_router
from app.communities.router import communities_router
from app.config import settings
from app.events.router import events_router

logging.basicConfig(level=logging.INFO)

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(communities_router, prefix="/communities")
api_router.include_router(events_router, prefix="/events")


app = FastAPI(
    title="Nitty",
    description="Professional Communities but fun",
    version="0.1.0",
)

app.include_router(api_router, prefix=settings.API_V1_STR)
