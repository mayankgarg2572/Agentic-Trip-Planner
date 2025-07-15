from app.models.schemas import ChatResponse, ItineraryResponse
from typing import Dict, Any

def parse_final_agent_state(agent_state: Dict[str, Any]) -> ChatResponse:
    """
    Parses final LangGraph agent state into structured ChatResponse.

    Args:
        agent_state: The final state dictionary returned by the LangGraph agent.

    Returns:
        ChatResponse: Structured final response for the frontend.
    """
    itinerary_response = agent_state.get("itinerary_response")
    verification = agent_state.get("final_verification")

    if itinerary_response and verification and verification.verified:
        return ChatResponse(
            status="success",
            itinerary=itinerary_response
        )
    else:
        return ChatResponse(
            status="failure",
            itinerary=ItineraryResponse(
                final_text="Unable to generate a verified itinerary.",
                ui_commands=[],
                budget_table=[]
            )
        )
