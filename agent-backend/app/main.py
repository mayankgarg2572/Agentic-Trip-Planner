from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1 import api_router
from dotenv import load_dotenv
from app.core.config import ALLOWED_ORIGINS
load_dotenv()
app = FastAPI(title="Agentic Trip Planner")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def check_agent_status(request: Request) -> dict:
    sample_response = {'status':'good'}
    return sample_response

app.include_router(api_router, prefix="/api/v1")


