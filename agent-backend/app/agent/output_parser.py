from app.models.schemas import BudgetTable, ChatResponse, ItineraryResponse
from typing import Dict, Any

def parse_final_agent_state(agent_state: Dict[str, Any]) -> ChatResponse:
    """
    Parses final LangGraph agent state into structured ChatResponse.

    Args:
        agent_state: The final state dictionary returned by the LangGraph agent.

    Returns:
        ChatResponse: Structured final response for the frontend.
    """
    itinerary_response = ItineraryResponse(
        final_text=agent_state.get("chat_response") or "",
        locations = agent_state.get("location_to_mark_on_ui") or [],
        budget_table = agent_state.get("budget_table") or BudgetTable(total_budget=0)
        )
    verification = agent_state.get("verified")

    if itinerary_response and verification:
        return ChatResponse(
            status="success",
            itinerary=itinerary_response
        )
    else:
        return ChatResponse(
            status="failure",
            itinerary=ItineraryResponse(
                final_text="Unable to generate a verified itinerary.",
                locations=[],
                budget_table=BudgetTable(total_budget=0)
            )
        )
