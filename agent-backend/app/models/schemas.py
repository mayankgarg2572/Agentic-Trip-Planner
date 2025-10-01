from pydantic import BaseModel
from typing import List, Optional, Dict 
from enum import Enum

class BaseLocType(Enum):
    tourist_spot = 'tourist_spot'
    destination = 'destination'
    accommodation = 'accommodation'

class GeoCodeType(Enum):
    city = "city"
    amenity="amenity"
    locality="locality"
    street="street"
    unknown="unknown"



class Location(BaseModel):
    address: str
    lat: float
    lng: float
    uuid: str


class BaseLocInfo(BaseModel):
    name: str
    type: BaseLocType


class GeoAPILocInput(BaseModel):
    name_original: str
    name_canonical: str 
    geocode_type: GeoCodeType = GeoCodeType.unknown
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    locality: Optional[str] = None
    inside_of: Optional[str] = None
    nearby: Optional[str] = None
    geocode_text: str
    sources:  List[str] = []

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

class userSpecifiedLocation(BaseModel):
    title: str
    lat: float
    lng: float
    # coordinates: List[str]  # List of "lat,lng" strings

class ChatRequest(BaseModel):
    prompt: str
    locations_Selected: Optional[List[userSpecifiedLocation]] = []


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
