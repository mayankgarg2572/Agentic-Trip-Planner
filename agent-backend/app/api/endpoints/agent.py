from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.agent.graph import compiled_agent_graph
from app.agent.output_parser import parse_final_agent_state

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    # Initial agent state
    initial_state = {"chat_request": request}

    # Execute LangGraph pipeline explicitly
    final_agent_state = compiled_agent_graph.invoke(initial_state)

    # Explicitly parse final agent state to structured response
    structured_response = parse_final_agent_state(final_agent_state)

    return structured_response
