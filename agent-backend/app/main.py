from fastapi import FastAPI
from app.api.api_v1 import api_router

app = FastAPI(title="Agentic Trip Planner")

app.include_router(api_router, prefix="/api/v1")
