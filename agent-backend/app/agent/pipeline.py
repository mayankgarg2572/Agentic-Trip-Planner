from app.utils.llm import MAIN_LLM
from app.services.directions import fetch_routes_metadata
from app.services.web_search import web_search_service
from langchain.tools import Tool
from app.models.schemas import BudgetItem
from app.services.geoapify import geocode_locations_service
import json
from app.agent.prompts import (
    LOCATION_EXTRACTION_PROMPT,
    ROUTE_ORDER_PROMPT,
    BUDGET_ESTIMATION_PROMPT,
    TIME_OPENING_FINDER,
    ROUTE_RECOMMENDATION_PROMPT
)
from typing import Any, Dict, List


def llm_with_web_search(prompt, llm, max_loops=2):
    final_content = [""]
    for _ in range(max_loops):
        result = llm.invoke(prompt)
        print(f"\n\nInside llm_with_web_searchResult:\n\n{result.content}")
        content = result.content if hasattr(result, "content") else str(result)
        content = content.strip()
        if content.startswith("search:"):
            content = content.replace('"', '').replace("'", '')
            search_query = content[len("search:"):].strip()
            # also need to remove the things like " or ' or from the content
            search_results = web_search_service(search_query)
            final_content+=search_results
            prompt += f"\n\nWeb search results for '{search_query}': {search_results}\nNow, based on this, continue."
        elif content.startswith("final_response:"):
            return content[len("final_response:"):].strip()
        else:
            return content
    print("Not able to complete the web search too much calls, returining:", final_content)
    return " ".join(final_content)

def remove_json_prefix_list(content: str) -> List[Any]:
    if isinstance(content, str):
        content = content.strip()
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()
        try:
            locations = json.loads(content)
            return locations
        except Exception:
            return []
    elif isinstance(content, list):
        return content
    else:
        return []


def extract_locations(user_query: str):
    print("\n\nInside the extract_locations function")
    llm = MAIN_LLM  # No need to bind tools
    prompt = (
        LOCATION_EXTRACTION_PROMPT +
        f"\nUser query: {user_query}\n"
    )
    content = llm_with_web_search(prompt, llm)
    locations = remove_json_prefix_list(content)
    
    print("\nCompleted extract_location function, with final locations:", locations)
    return locations

def extract_suitable_time(user_query: str, locations: list[dict]) -> str:
    print("\n\nInside the extract_suitable_time function")

    llm = MAIN_LLM
    prompt = TIME_OPENING_FINDER + "\n\nUser query:" + f"{user_query}\n\nLocations: {locations}."

    result = llm_with_web_search(prompt, llm)
    print("\nCompleted extract_suitable_time function call")
    timings = remove_json_prefix_list(result)
    return str(timings) if timings is not None else ""



def order_locations(location_objs, routes, suitable_time_opening, user_query):
    print("\n\nInside the order_locations function call")
    llm = MAIN_LLM
    names = [loc.address for loc in location_objs]
    prompt = ROUTE_ORDER_PROMPT + f"\n\nUser query: {user_query}\n\nLocations: {names}\n\nRoutes General info between different Locations:{routes}\n\nSuitable opening times of tourists spots: {suitable_time_opening}"
    result = llm.invoke(prompt)

    result = llm_with_web_search(prompt, llm)
    ordered_names = remove_json_prefix_list(result)
    
    ordered = [loc for name in ordered_names for loc in location_objs if loc.address == name]
    print("\nCompleted order_locations function call")
    return ordered



def estimate_budget(user_query, location_objs):
    print("\n\nInside estimate_budget function call")

    llm = MAIN_LLM
    budget_items = []
    total_budget = 0
    for loc in location_objs:
        prompt = BUDGET_ESTIMATION_PROMPT + f"\n\nLocation: {loc.address}\n\nUser query: {user_query}"
        result = llm_with_web_search(prompt, llm)
        items = remove_json_prefix_list(result)
        for item in items:
            reason = getattr(item, 'item', item.get('item') if isinstance(item, dict) else None)
            if reason is None:
                reason = ""
            amount = getattr(item, 'cost', item.get('cost') if isinstance(item, dict) else None)
            if amount is None:
                amount = 0
            budget_items.append(BudgetItem(reason=str(reason), amount=amount))
            total_budget += amount
    print("\nCompleted estimated_budget function call")
    return budget_items, total_budget

def node1_pipeline(user_query: str):
    print("\n\nInside the node1_pipeline function call")
    # 1. Extract locations (LLM + web_search)
    locations_info = extract_locations(user_query)
    
    # Ensure only dict elements are passed to extract_suitable_time
    filtered_locations_info = [loc for loc in locations_info if isinstance(loc, dict)]
    suitable_time_opening = extract_suitable_time(user_query, filtered_locations_info)

    # 2. Geocode locations
    location_objs = geocode_locations_service(locations_info)
    
    # 3. Fetch routes
    routes = fetch_routes_metadata(location_objs)

    # 4. Order locations (LLM + web_search)
    ordered_locations = order_locations(location_objs, routes, suitable_time_opening, user_query)
    
    # 5. Estimate budget (LLM + web_search)
    budget_items, total_budget = estimate_budget(user_query, ordered_locations)

    prompt = ROUTE_RECOMMENDATION_PROMPT + f"\n\nUser query:{user_query},\n\nThe different Location's info as related to the user query are:{locations_info}\n\nFinal Ordered Route:{ordered_locations}\n\nEstimated Budget:{budget_items}."
    final_chat_response = MAIN_LLM.invoke(prompt)

    # 6. Format response
    response = {
        "location_to_mark_on_ui": [loc.dict() for loc in ordered_locations],
        "location_order_for_showing_route_on_ui": [str(loc.uuid) for loc in ordered_locations],
        "chat_response": final_chat_response.content,
        "budget_table": {
            "total_budget": total_budget,
            "budget_breakdown": [item.dict() for item in budget_items]
        }
    }
    print("\nCompleted node1_pipeline function call")
    return response