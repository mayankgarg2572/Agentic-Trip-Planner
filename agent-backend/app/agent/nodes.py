from app.models.schemas import (
    ChatRequest, RequiredOperations, ExtractedData, 
    ItineraryResponse, VerificationResult
)
from typing import Dict, Any

class RequirementAnalysisNode:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze user prompt to determine required operations.
        Updates state['required_operations'].
        """

class DataExtractionNode:
    def __init__(self, geoapify_service, directions_service, web_search_service):
        self.geoapify_service = geoapify_service
        self.directions_service = directions_service
        self.web_search_service = web_search_service

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data required by itinerary node.
        Updates state['extracted_data'].
        """

class ItineraryGenerationNode:
    def __init__(self, llm, web_service):
        self.llm = llm
        self.web_service = web_service
        # self.fetch_expenses_service = fetch_expenses
        # self.fetch_tourist_info_service = fetch_tourist_info

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate optimized itinerary, handle expenses and web search.
        If invalid data detected, update state['required_operations']
        and state['fallback_counts'] accordingly.
        Updates state['itinerary_response'].
        """

class ResponseVerifierNode:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify final itinerary response, handle retries explicitly.
        Updates state['final_verification'] and state['fallback_counts'].
        """


class LocationFinderNode:
    def __init__(self, llm, geoapify_service):
        self.llm = llm
        self.llm.bind_tools([geoapify_service])
        # self.geoapify_service = geoapify_service

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Geocode addresses using Geoapify service.
        Updates state['extracted_data']['locations'] with geocoded results.
        """
        addresses = state['extracted_data'].get('addresses', [])
        prompt = "You are a location finder. Based on the provided addresses, find their geographical coordinates. Return a list of locations with latitude and longitude. Do not return any other information. For example, for 'Eiffel Tower, Paris', return {'address': 'Eiffel Tower, Paris', 'lat': 48.8584, 'lng': 2.2945}. Here are the addresses: " + ", ".join(addresses)
        locations = self.llm.invoke(prompt)
        state['extracted_data']['locations'] = locations
        return state

class RouteFinderNode:
    def __init__(self, llm, directions_service):
        self.llm = llm
        self.llm.bind_tools([directions_service])
        # self.directions_service = directions_service

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch routes metadata using Directions service.
        Updates state['extracted_data']['routes'] with fetched routes.
        """
        locations = state['extracted_data'].get('locations', [])
        prompt = "You are a route finder. You have access for a tool which will accept two locations. Now you will be provided with two locations. Based on those locations, find the best routes from location A to location B. Return a list of routes with details. For input:{ location A: {'Eiffel Tower, Paris', location B: 'Louvre Museum, Paris'. Your result should have format: {locations:{ A:{lat: <lat>, lng: <lng>}, B:{lat: <lat>, lng: <lng>} }, Distance_in_km:2313  , Average_Time_in_minutes:234  }   Here are the locations: " + ", ".join(locations)
        routes = self.llm.invoke(prompt)
        state['extracted_data']['routes'] = routes
        return state