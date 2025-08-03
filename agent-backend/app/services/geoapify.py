import httpx
from typing import List
from app.models.schemas import Location
from app.utils.helpers import generate_uuid
from app.core.config import GEOAPIFY_API_KEY

def geocode_addresses(addresses: List[str]) -> List[Location]:
    print("\n\nInside geocode_addresses function")
    results = []
    for address in addresses:
        url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={GEOAPIFY_API_KEY}"
        data  = {}
        try:
            response = httpx.get(url)
            data = response.json()
            response.raise_for_status()
        except Exception as e:
            print("Getting error in extracting location coordi, for location:", address, "\nError is:", e)
            continue

        if data and data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            results.append(Location(address=address, lat=coords[1], lng=coords[0], uuid = generate_uuid()))
        else:
            print("Not able to extract location coordi, for location:", address, "\nThe api(extract_location_coordinate) response was:", data)
            continue
    print("\nCompleted function geocode_addresses")
    return results


def geocode_locations_service(locations): 
    """
    This function accepts a list of location dictionaries with 'name' keys,
    and returns a list of Location objects with geocoded coordinates.
    Args:
        locations (List[dict]): A list of location dictionaries.
    
    Returns:
        List[Location]: A list of Location objects with geocoded coordinates.
    """

    print("\n\nInside geocode_locations_service function")
    addresses = [loc['name'] for loc in locations]
    geo_results = geocode_addresses(addresses)
    print("\nCompleted geocode_location_service_function")
    return geo_results