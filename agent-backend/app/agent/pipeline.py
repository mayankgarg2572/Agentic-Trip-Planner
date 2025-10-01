from hmac import new
from exceptiongroup import catch
from app.utils.llm import MAIN_LLM
from app.services.directions import fetch_complete_itinerary, fetch_routes_metadata
from app.services.web_search import web_search_service
from langchain.tools import Tool
from app.models.schemas import BaseLocInfo, BudgetItem, GeoAPILocInput, userSpecifiedLocation
from app.services.geoapify import geocode_locations_service, reverse_geocode_coordinates
import json
from app.agent.prompts import (
    LOCATION_EXTRACTION_PROMPT,
    GEOAPIFY_INPUT_PREP_PROMPT,
    ROUTE_ORDER_PROMPT,
    BUDGET_ESTIMATION_PROMPT,
    TIME_OPENING_FINDER,
    ROUTE_RECOMMENDATION_PROMPT
)
from typing import Any, Dict, List, Optional


def llm_with_web_search(prompt, llm, max_loops=2):
    final_content = [""]
    print(f"Inside llm_with_web_search")
    for _ in range(max_loops+1):
        
        result = llm.invoke(prompt)
        
        content = result.content if hasattr(result, "content") else str(result)
        content = content.strip()
        if content.startswith("search:"):
            content = content.replace('"', '').replace("'", '')
            search_query = content[len("search:"):].strip()
            # also need to remove the things like " or ' or from the content
            search_results = web_search_service(search_query)
            final_content+=search_results
            if _ == max_loops -1 :
                prompt += f"\n\nWeb search results for '{search_query}': {search_results}\n\n\nNow, since this was your final query, now please craft the response for the asked task and the response must be in the specified format only."

            else:
                prompt += f"\n\nWeb search results for '{search_query}': {search_results}\nNow, based on this, continue."
        elif content.startswith("final_response:"):
            return content[len("final_response:"):].strip()
        else:
            return content
    print("Not able to complete the web search, too much calls, sample final content(max 3):", final_content[:min(len(final_content), 3)])
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


from collections.abc import Mapping

def to_base_loc(loc) -> Optional[BaseLocInfo]:
    if isinstance(loc, BaseLocInfo):
        return loc
    if hasattr(loc, "name") and hasattr(loc, "type"):
        return BaseLocInfo(name=loc.name, type=loc.type)
    if isinstance(loc, Mapping) and "name" in loc and "type" in loc:
        return BaseLocInfo(name=loc["name"], type=loc["type"])
    return None  # fallback: leave as-is

def extract_locations(user_query: str) -> List[BaseLocInfo]:
    print("\n\nInside the extract_locations function")
    llm = MAIN_LLM  
    prompt = (
        LOCATION_EXTRACTION_PROMPT +
        f"\nUser query: {user_query}\n"
    )
    try:

        content = llm_with_web_search(prompt, llm)
        locations = remove_json_prefix_list(content)
        locations =  [BaseLocInfo(**loc) for loc in locations if isinstance(loc, dict) and "name" in loc and "type" in loc]
        return locations
    except Exception as e:
        print("Error occurred while extracting locations:", e)
        raise e

    


def format_locations(user_query:str, locations: List[BaseLocInfo]) -> List[GeoAPILocInput]:
    print("\n\nInside the format_locations function")
    llm = MAIN_LLM  
    prompt = (
        GEOAPIFY_INPUT_PREP_PROMPT +
        f"\nUser query: {user_query}"+
        f"\n\n Locations: {locations}"
    )
    try:
        content = llm_with_web_search(prompt, llm)
        new_locations = remove_json_prefix_list(content)
        new_locations = [
            GeoAPILocInput(**loc) for loc in new_locations
            if isinstance(loc, dict) and
                "name_canonical" in loc and loc["name_canonical"] and
                "geocode_text" in loc and loc["geocode_text"] and
                "name_original" in loc and loc["name_original"]
        ]
        return new_locations
    except Exception as e:
        print("Error occurred while formatting locations:", e)
        raise e


def extract_suitable_time(user_query: str, locations: list[GeoAPILocInput]) -> str:
    print("\n\nInside the extract_suitable_time function")

    llm = MAIN_LLM
    prompt = TIME_OPENING_FINDER + "\n\nUser query:" + f"{user_query}\n\nLocations: {locations}."
    
    try:
        result = llm_with_web_search(prompt, llm)
        timings = remove_json_prefix_list(result)
    except Exception as e:
        print("Error occurred while extracting suitable time:", e)
        timings = None
    return str(timings) if timings is not None else ""


def order_locations(location_objs, routes, suitable_time_opening, user_query):
    print("\n\nInside the order_locations function call")
    llm = MAIN_LLM
    names = [loc.address for loc in location_objs]
    prompt = ROUTE_ORDER_PROMPT + f"\n\nUser query: {user_query}\n\nLocations: {names}\n\nRoutes General info between different Locations:{routes}\n\nSuitable opening times of tourists spots: {suitable_time_opening}"
    result = llm.invoke(prompt)
    try:
        result = llm_with_web_search(prompt, llm)
        ordered_names = remove_json_prefix_list(result)
        ordered = [loc for name in ordered_names for loc in location_objs if loc.address == name]
        return ordered
    except Exception as e:
        print("Error occurred while ordering locations:", e)
        raise e


def estimate_budget(user_query, location_objs):
    print("\n\nInside estimate_budget function call")
    llm = MAIN_LLM
    budget_items = []
    total_budget = 0
    try:
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
        return budget_items, total_budget
    except Exception as e:
        print("Error occurred while estimating budget:", e)
        return budget_items, total_budget


def node1_pipeline(user_query: str, user_provided_locations: Optional[List[userSpecifiedLocation]] = []):
    print("\n\nInside the node1_pipeline function")

    try:
        # 0. Extract user specified locations if any
        if user_provided_locations and len(user_provided_locations) > 0:
            location_objs = reverse_geocode_coordinates(user_provided_locations)
            user_query += "Some possible address of the specified locations are: " + ", ".join([f'Location no. {i}:  {loc.address}\n' for i, loc in enumerate(location_objs)])

        # 1. Extract locations (LLM + web_search)
        locations_info = extract_locations(user_query)
        print("Final Extracted Locations info:", locations_info)

        final_locations_info = format_locations(user_query, locations_info)
        print("Final Formatted Locations info:", final_locations_info)

        suitable_time_opening = extract_suitable_time(user_query, final_locations_info)

        # 2. Geocode locations
        location_objs = geocode_locations_service(final_locations_info)
        print("The extracted geo coordinates:", location_objs)    
        # 3. Fetch routes
        routes = fetch_routes_metadata(location_objs)

        complete_itineraries = fetch_complete_itinerary(location_objs)
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
            },
            "api_result_itineraries": complete_itineraries
        }
    except Exception as e:
        print("Getting error in node1_pipeline:", e)
        response = {
            "location_to_mark_on_ui": [],
            "location_order_for_showing_route_on_ui": [],
            "chat_response": f"Sorry, an error occurred while processing your request: {e}",
            "budget_table": {
                "total_budget": 0,
                "budget_breakdown": []
            },
            "api_result_itineraries": []
        }
    return response