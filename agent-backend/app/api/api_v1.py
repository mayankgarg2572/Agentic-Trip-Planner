from fastapi import APIRouter
from app.api.endpoints.agent import router as agent_router

api_router = APIRouter()
api_router.include_router(agent_router, prefix="/agent", tags=["agent"])
