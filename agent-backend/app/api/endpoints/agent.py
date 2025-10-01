from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.agent.graph import compiled_agent_graph
from app.agent.output_parser import parse_final_agent_state
from app.agent.graph import AgentState

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest) -> ChatResponse:
    # print("\n\nReceived request at /chat endpoint with data:", request)
    final_agent_state = compiled_agent_graph.invoke(
        AgentState(
            user_query=request.prompt, 
            user_specified_locations_coords=getattr(request, "locations_Selected", None)
        )
    )

    structured_response = parse_final_agent_state(final_agent_state)

    return structured_response
