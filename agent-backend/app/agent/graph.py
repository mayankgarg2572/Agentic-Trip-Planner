from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from typing import List, Optional
from app.agent.nodes import ExtractionGenerationNode, VerificationNode
from app.models.schemas import Location

class BudgetElement(BaseModel):
    item: str
    cost: float

class AgentState(BaseModel):
    user_query: str = ""
    location_to_mark_on_ui: List[Location] = []
    location_order_for_showing_route_on_ui: List[str] = []
    chat_response: str = ""
    budget_table: dict = {
        "total_budget": 0,
        "budget_breakdown": []
    }
    fallback_count: int = 0

# Instantiate nodes
extraction_generation_node = ExtractionGenerationNode()
verification_node = VerificationNode()

def verification_conditional(state: AgentState) -> str:
    if getattr(state, "verified", False):
        return "end"
    elif state.fallback_count < 2:
        state.fallback_count += 1
        return "retry_extraction_generation"
    else:
        return "end"

agent_graph = StateGraph(AgentState)
agent_graph.add_node("extraction_generation", extraction_generation_node)
agent_graph.add_node("verification", verification_node)
agent_graph.set_entry_point("extraction_generation")
agent_graph.add_edge("extraction_generation", "verification")
agent_graph.add_conditional_edges(
    "verification",
    verification_conditional,
    {
        "retry_extraction_generation": "extraction_generation",
        "end": END
    }
)
compiled_agent_graph = agent_graph.compile()