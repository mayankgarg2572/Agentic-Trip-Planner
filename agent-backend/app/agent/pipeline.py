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
    BUDGET_ESTIMATION_PROMPT
)


def extract_locations(user_query: str):
    print("\n\nInside the extract_locations function")
    web_search_tool = Tool.from_function(
        web_search_service,
        name="web_search",
        description="Search the web for up-to-date information about locations, travel tips, and other relevant data."
    )
    llm = MAIN_LLM.bind_tools([web_search_tool])
    prompt = LOCATION_EXTRACTION_PROMPT + f"\nUser query: {user_query}\nIf you need more info about a place, use the web_search tool."
    result = llm.invoke(prompt)
    # Parse result as list of dicts [{"name": ..., "type": ...}]
    content = result.content
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
        except Exception:
            locations = []
    elif isinstance(content, list):
        locations = content
    else:
        locations = []
    print("\nCompleted extract_location function")
    return locations

def extract_suitable_time(user_query: str, locations: list[dict]) -> str:
    """
    Extract suitable travel times for tourist spots as asked in the user query.
    Args:
        user_query (str): The user's query asking for travel times.
        locations (list[dict]): List of locations to consider.
    Returns:
        str: A string with suitable travel times for the tourist spots.
    """
    print("\n\nInside the extract_suitable_time function")
    web_search_tool = Tool.from_function(
        web_search_service,
        name="web_search",
        description="Search the web for up-to-date information about locations, travel tips, and other relevant data."
    )
    llm = MAIN_LLM.bind_tools([web_search_tool])
    format  = "[{location_name: 'sample_location', suitable_time:'10::00AM - 12:30PM,3:30PM-5:30PM'}]"
    prompt = "Extract suitable travel times for tourist spots as asked in the user query:" + f"{user_query} from the locations: {locations}. Here a lot of location are provided, just choose which are suitable as per the user query like tourist spots etc..\n\n\nUse web_search if you need to know best times or travel tips. Provide the final result in JSON only in the format as below:{format}" 
    
    result = llm.invoke(prompt)
    print("\nCompleted extract_suitable_time function call")
    return str(result.content) if result.content is not None else ""



def order_locations(location_objs, routes, suitable_time_opening, user_query):
    print("\n\nInside the order_locations function call")
    web_search_tool = Tool.from_function(
        web_search_service,
        name="web_search",
        description="Search the web for up-to-date information about locations, travel tips, and other relevant data."
    )
    llm = MAIN_LLM.bind_tools([web_search_tool])
    names = [loc.address for loc in location_objs]
    prompt = ROUTE_ORDER_PROMPT + f"\nUser query: {user_query}\n\nLocations: {names}\n\n Routes General info between different Locations:{routes}\n\nSuitable opening times: {suitable_time_opening}\n\nUse web_search if you need to know best order or travel tips."
    result = llm.invoke(prompt)
    content = result.content
    if isinstance(content, str):
        content = content.strip()
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()
        try:
            ordered_names = json.loads(content)
        except Exception:
            ordered_names = []
    elif isinstance(content, list):
        ordered_names = content
    else:
        ordered_names = []
    ordered = [loc for name in ordered_names for loc in location_objs if loc.address == name]
    print("\nCompleted order_locations function call")
    return ordered



def estimate_budget(user_query, location_objs):
    print("\n\nInside estimate_budget function call")
    web_search_tool = Tool.from_function(
        web_search_service,
        name="web_search",
        description="Search the web for up-to-date information about locations, travel tips, and other relevant data."
    )
    llm = MAIN_LLM.bind_tools([web_search_tool])
    budget_items = []
    total_budget = 0
    for loc in location_objs:
        prompt = BUDGET_ESTIMATION_PROMPT + f"\nLocation: {loc.address}\nUser query: {user_query}\nUse web_search for up-to-date prices and recommendations."
        result = llm.invoke(prompt)
        # items = items.content
        content = result.content
        if isinstance(content, str):
            content = content.strip()
            if content.startswith("```json"):
                content = content[len("```json"):].strip()
            if content.startswith("```"):
                content = content[len("```"):].strip()
            if content.endswith("```"):
                content = content[:-len("```")].strip()
            try:
                items = json.loads(content)
            except Exception:
                items = []
        elif isinstance(content, list):
            items = content
        else:
            items = []
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

    prompt = f"For the provided user query:{user_query}, the information generated for the user is Location's info:{locations_info}\n\n Final Ordered Route:{ordered_locations} Estimated Budget:{budget_items}. Support how well the generated response able to answer the asked query. Explain the generated information in respect of user's query."
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