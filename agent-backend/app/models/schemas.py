from pydantic import BaseModel
from typing import List, Optional, Dict

class Location(BaseModel):
    address: str
    lat: float
    lng: float
    uuid: str

class RouteMetadata(BaseModel):
    from_location: str
    to_location: str
    distance_km: float
    travel_time_min: float

class ExpenseMetadata(BaseModel):
    transportation_costs: Dict[str, float]
    meals_avg_cost: float
    ticket_prices: Dict[str, float]

class TouristInfo(BaseModel):
    place_name: str
    opening_time: str
    closing_time: str

class RequiredOperations(BaseModel):
    need_locations: bool
    need_routes: bool
    need_expenses: bool
    need_tourist_info: bool

class ChatRequest(BaseModel):
    prompt: str
    existing_markers: Optional[List[Location]]


class BudgetItem(BaseModel):
    reason: str
    amount: float

class BudgetTable(BaseModel):
    total_budget:int | float
    budget_breakdown:List[BudgetItem] = []

class ItineraryResponse(BaseModel):
    final_text: str
    locations: List[Location]
    budget_table: BudgetTable

class VerificationResult(BaseModel):
    verified: bool
    feedback: Optional[str]

class ChatResponse(BaseModel):
    status: str
    itinerary: ItineraryResponse
    api_result_itineraries: object | None

class ExtractedData(BaseModel):
    locations: List[Location]
    routes_metadata: List[RouteMetadata]
    expenses_metadata: ExpenseMetadata
    tourist_info: List[TouristInfo]
