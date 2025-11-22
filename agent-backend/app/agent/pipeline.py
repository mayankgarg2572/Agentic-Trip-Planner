from typing import List, Optional, Tuple
from langsmith import traceable

from app.models.schemas import BaseLocInfo, BudgetItem, GeoAPILocInput, userSpecifiedLocation

from app.services.directions import build_pairwise_air_distance, fetch_complete_itinerary
from app.services.web_search import llm_with_web_search
from app.services.geoapify import geocode_locations_service, reverse_geocode_coordinates

from app.agent.prompts import (
    LOCATION_EXTRACTION_PROMPT,
    GEOAPIFY_INPUT_PREP_PROMPT,
    ROUTE_ORDER_PROMPT,
    BUDGET_ESTIMATION_PROMPT,
    TIME_OPENING_FINDER,
    ROUTE_RECOMMENDATION_PROMPT
)

from app.utils.clean_load_json import remove_json_prefix_list, _PARSE_FAILED
from app.utils.helpers import correct_final_llm_response_format
from app.utils.llm import MAIN_LLM

@traceable
def extract_locations(user_query: str) -> List[BaseLocInfo]:
    print("\n\nInside the extract_locations function")
    llm = MAIN_LLM  
    prompt = (
        LOCATION_EXTRACTION_PROMPT +
        f"\nUser query: {user_query}\n"
    )
    try:
        content = llm_with_web_search(prompt, llm)
        result = remove_json_prefix_list(content)
        locations = [] if (result is _PARSE_FAILED) else result
        locations =  [BaseLocInfo(**loc) for loc in locations if isinstance(loc, dict) and "name" in loc and "type" in loc]
        return locations
    except Exception as e:
        print("Error occurred while extracting locations:", e)
        raise e

@traceable
def format_locations(user_query:str, locations: List[BaseLocInfo]) -> List[GeoAPILocInput]:
    print("\n\nInside the format_locations function")
    if len(locations) == 0:
        return []
    llm = MAIN_LLM  
    prompt = (
        GEOAPIFY_INPUT_PREP_PROMPT +
        f"\nUser query: {user_query}"+
        f"\n\n Locations: {locations}"
    )
    try:
        content = llm_with_web_search(prompt, llm)
        result = remove_json_prefix_list(content)
        new_locations = [] if (result is _PARSE_FAILED) else result
        
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

@traceable
def extract_suitable_time(user_query: str, locations: list[GeoAPILocInput]) -> str:
    print("\n\nInside the extract_suitable_time function")
    if len(locations) == 0:
        return ""
    llm = MAIN_LLM
    prompt = TIME_OPENING_FINDER + "\n\nUser query:" + f"{user_query}\n\nLocations: {locations}."
    
    try:
        content = llm_with_web_search(prompt, llm)
        result = remove_json_prefix_list(content)
        timings = [] if (result is _PARSE_FAILED) else result
        
    except Exception as e:
        print("Error occurred while extracting suitable time:", e)
        timings = None
    return str(timings) if timings is not None else ""

@traceable
def order_locations(location_objs, routes, suitable_time_opening, user_query):
    print("\n\nInside the order_locations function call")
    if len(location_objs) == 0:
        return []
    llm = MAIN_LLM
    names = [loc.address for loc in location_objs]
    prompt = ROUTE_ORDER_PROMPT + f"\n\nUser query: {user_query}\n\nLocations: {names}\n\nRoutes General info between different Locations:{routes}\n\nSuitable opening times of tourists spots: {suitable_time_opening}"
    result = llm.invoke(prompt)
    try:
        content = llm_with_web_search(prompt, llm)
        result = remove_json_prefix_list(content)
        ordered_names = [] if (result is _PARSE_FAILED) else result
        ordered = [loc for name in ordered_names for loc in location_objs if loc.address == name]
        return ordered
    except Exception as e:
        print("Error occurred while ordering locations:", e)
        raise e

@traceable
def estimate_budget(user_query, location_objs) -> Tuple[List[BudgetItem], int] :
    print("\n\nInside estimate_budget function call")
    if len(location_objs) == 0:
        return [], -1
    llm = MAIN_LLM
    budget_items = []
    total_budget = 0
    try:
        for loc in location_objs:
            prompt = BUDGET_ESTIMATION_PROMPT + f"\n\nLocation: {loc.address}\n\nUser query: {user_query}"
            content = llm_with_web_search(prompt, llm)
            result = remove_json_prefix_list(content)
            items = [] if (result is _PARSE_FAILED) else result
            
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
        print("Locations result1:", locations_info)

        final_locations_info = format_locations(user_query, locations_info)
        print("Locations result2:", final_locations_info)

        suitable_time_opening = extract_suitable_time(user_query, final_locations_info)
        
        # 2. Geocode locations
        location_objs = geocode_locations_service(final_locations_info)
  
        # 3. Fetch routes
        routes = build_pairwise_air_distance(location_objs)

        # 4. Order locations (unchanged call)
        ordered_locations = order_locations(location_objs, routes, suitable_time_opening, user_query)

        # (Optional, precise legs for UI or final prompt)
        # final_leg_routes = fetch_routes_metadata(ordered_locations, adjacent_only=True)

        complete_itineraries = fetch_complete_itinerary(location_objs)

        
        # 5. Estimate budget (LLM + web_search)
        budget_items, total_budget = estimate_budget(user_query, ordered_locations)

        prompt = ROUTE_RECOMMENDATION_PROMPT + f"\n\nUser query:{user_query},\n\nThe different Location's info as related to the user query are:{locations_info}\n\nFinal Ordered Route:{ordered_locations}\n\nEstimated Budget:{budget_items}."
        final_chat_response = MAIN_LLM.invoke(prompt)

        # 6. Format response
        response = {
            "location_to_mark_on_ui": [loc.dict() for loc in ordered_locations],
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
            "chat_response": f"Sorry, an error occurred while processing your request: {e}",
            "budget_table": {
                "total_budget": 0,
                "budget_breakdown": []
            },
            "api_result_itineraries": []
        }
    return response