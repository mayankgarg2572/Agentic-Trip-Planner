from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.agent.graph import compiled_agent_graph
from app.agent.output_parser import parse_final_agent_state
from app.agent.graph import AgentState

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    final_agent_state = compiled_agent_graph.invoke(AgentState(user_query = request.prompt))

    structured_response = parse_final_agent_state(final_agent_state)

    return structured_response
