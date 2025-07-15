import httpx
from typing import List
from app.models.schemas import Location, RouteMetadata
from app.core.config import GEOAPIFY_API_KEY

def fetch_routes_metadata(locations: List[Location]) -> List[RouteMetadata]:
    """
    Fetches the best routes between every two locations provided in the locations' array

    Args:
    
    """
    print("\n\nInside the fetch_route_metadata function")
    route_metadata = []
    cur_url = f"https://api.geoapify.com/v1/routing?waypoints="
    for i, origin in enumerate(locations):
    #     if i == len(locations)-1:
    #         cur_url+=f'{origin.lat},{origin.lng}'
    #     else:
    #         cur_url+=f'{origin.lat},{origin.lng}|'
    # cur_url+=f"&mode=drive&apiKey={GEOAPIFY_API_KEY}"
    
        for j, dest in enumerate(locations):
            if i != j:
                url = (
                    f"https://api.geoapify.com/v1/routing"
                    f"?waypoints={origin.lat},{origin.lng}|{dest.lat},{dest.lng}"
                    f"&mode=drive&apiKey={GEOAPIFY_API_KEY}"
                )
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
    # response = httpx.get(cur_url)
    # response.raise_for_status()
    # data = response.json()
    print("\nReturning from fetch_route_metadata function")
    # return data
    return route_metadata


