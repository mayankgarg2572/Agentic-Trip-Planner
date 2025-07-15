from typing import Optional
from langgraph.graph import StateGraph, END
from pydantic import BaseModel
from app.agent.nodes import (
    RequirementAnalysisNode,
    DataExtractionNode,
    ItineraryGenerationNode,
    ResponseVerifierNode
)

from app.models.schemas import (
    ChatRequest,
    RequiredOperations,
    ExtractedData,
    ItineraryResponse,
    VerificationResult
)
from app.services.geoapify import geocode_addresses  
from app.services.directions import fetch_routes_metadata
from app.services.web_search import web_search_service
from app.services.database import save_verified_locations
from app.utils.llm import MAIN_LLM, GRAPH_LLM

# Condition functions
def check_itinerary_data(state: dict) -> str:
    """
    Determines if fallback to DataExtractionNode is required
    due to invalid or incomplete data.
    """
    fallback_counts = state["fallback_counts"]["data_extraction"]
    data_valid = state["itinerary_response"].data_valid  # Explicitly defined by itinerary node
    if not data_valid and fallback_counts < 2:
        state["fallback_counts"]["data_extraction"] += 1
        return "retry_data_extraction"
    return "continue_verification"

def check_final_verification(state: dict) -> str:
    """
    Determines if the response is verified or requires retry.
    """
    fallback_counts = state["fallback_counts"]["itinerary_generation"]
    verified = state["final_verification"].verified
    if verified:
        return "end"
    elif fallback_counts < 2:
        state["fallback_counts"]["itinerary_generation"] += 1
        return "retry_itinerary_generation"
    else:
        return "end"  # Explicitly terminate after max retries

# Initialize nodes explicitly
requirement_node = RequirementAnalysisNode(llm=MAIN_LLM)
data_extraction_node = DataExtractionNode(
    llm=MAIN_LLM,
    geoapify_service=geocode_addresses,
    directions_service=fetch_routes_metadata,
    web_search_service=web_search_service
)
itinerary_node = ItineraryGenerationNode(llm=GRAPH_LLM, web_search_service=web_search_service)
verifier_node = ResponseVerifierNode(llm=GRAPH_LLM, save_verified_locations=save_verified_locations)


class AgentState(BaseModel):
    chat_request: ChatRequest
    required_operations: Optional[RequiredOperations] = None
    extracted_data: Optional[ExtractedData] = None
    itinerary_response: Optional[ItineraryResponse] = None
    final_verification: Optional[VerificationResult] = None
    fallback_counts: dict = {
        "data_extraction": 0,
        "itinerary_generation": 0
    }

# Define State Graph explicitly
agent_graph = StateGraph(AgentState)

# Add Nodes explicitly
agent_graph.add_node("requirement_analysis", requirement_node)
agent_graph.add_node("data_extraction", data_extraction_node)
agent_graph.add_node("itinerary_generation", itinerary_node)
agent_graph.add_node("response_verification", verifier_node)

# Set Entry Point explicitly
agent_graph.set_entry_point("requirement_analysis")

# Explicit edges
agent_graph.add_edge("requirement_analysis", "data_extraction")
agent_graph.add_edge("data_extraction", "itinerary_generation")

# Conditional edge from itinerary_generation → data_extraction if data invalid
agent_graph.add_conditional_edges(
    "itinerary_generation",
    check_itinerary_data,
    {
        "retry_data_extraction": "data_extraction",
        "continue_verification": "response_verification"
    }
)

# Conditional edge from response_verification → itinerary_generation if verification fails
agent_graph.add_conditional_edges(
    "response_verification",
    check_final_verification,
    {
        "retry_itinerary_generation": "itinerary_generation",
        "end": END
    }
)

# Compile the graph explicitly
compiled_agent_graph = agent_graph.compile()
