import httpx
from typing import List
from app.models.schemas import Location, RouteMetadata
from app.core.config import GEOAPIFY_API_KEY
from math import radians, sin, cos, asin, sqrt

def _valid_coord(lat, lng):
    return (lat is not None and lng is not None and
            -90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0)


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat, dlon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2 * R * asin(sqrt(a))


def build_pairwise_air_distance(locations: list[Location]) -> list[RouteMetadata]:
    route_metadata = []
    if len(locations) < 2:
        return route_metadata
    for i, origin in enumerate(locations):
        if not _valid_coord(origin.lat, origin.lng):
            continue
        for j in range(i+1, len(locations)):
            dest = locations[j]
            if not _valid_coord(dest.lat, dest.lng):
                continue
            d = _haversine_km(origin.lat, origin.lng, dest.lat, dest.lng)
            # Rough time fallback for UI context; accurate times will come from API later
            route_metadata.append(RouteMetadata(
                from_location=origin.address,
                to_location=dest.address,
                distance_km=d,
                travel_time_min=(d / 40.0) * 60.0
            ))
    return route_metadata


def fetch_routes_metadata(locations: List[Location], adjacent_only: bool = False) -> List[RouteMetadata]:
    """
    Fetches the best routes between every two locations provided in the locations' array

    Args:
    
    """
    print("\n\nInside the fetch_route_metadata function")
    if len(locations) < 2:
        print("Not enough locations to fetch route metadata, locations:", locations)
        return []
    route_metadata = []

    if adjacent_only:
        pairs = [(locations[i], locations[i+1]) for i in range(len(locations)-1)]
    else:
        pairs = []
        for i in range(len(locations)):
            for j in range(i+1, len(locations)):
                pairs.append((locations[i], locations[j]))
    
    for origin, dest in pairs:
        if (not _valid_coord(origin.lat, origin.lng)) or (not _valid_coord(dest.lat, dest.lng)):
            continue
        url = (
            f"https://api.geoapify.com/v1/routing"
            f"?waypoints={origin.lat},{origin.lng}|{dest.lat},{dest.lng}"
            f"&mode=drive&apiKey={GEOAPIFY_API_KEY}"
        )
        try:
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()
            distance = data["features"][0]["properties"]["distance"]
            duration = data["features"][0]["properties"]["time"]
            route_metadata.append(RouteMetadata(
                from_location=origin.address,
                to_location=dest.address,
                distance_km=distance / 1000,
                travel_time_min=duration / 60
            ))
        except Exception as e:
            print(f"For origin:{origin},\nand destination:{dest}\ngetting error:", e)
    
    return route_metadata


def fetch_complete_itinerary(locations: List[Location]) -> object:
    """
    Fetches the complete itineraries
    """
    print("\n\nInside the fetch_complete_itinerary function")
    if len(locations) < 2:
        print("Not enough locations to fetch complete itinerary, locations:", locations)
        return None
    cur_url = f"https://api.geoapify.com/v1/routing?waypoints="
    for i, origin in enumerate(locations):
        if not _valid_coord(origin.lat, origin.lng):
            print("Finding negative coordinate for:", origin)
            continue

        if i == len(locations)-1:
            cur_url+=f'{origin.lat},{origin.lng}'
        else:
            cur_url+=f'{origin.lat},{origin.lng}|'
    cur_url+=f"&mode=drive&apiKey={GEOAPIFY_API_KEY}"
    
    try:
        response = httpx.get(cur_url)
        response.raise_for_status()
        data = response.json()
        
    except Exception as e:
        print(f"For complete itineraries finding, getting error:",e )
        return None
    return data


