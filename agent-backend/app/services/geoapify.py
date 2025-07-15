import httpx
from typing import List
from app.models.schemas import Location
from app.utils.helpers import generate_uuid
import os
from dotenv import load_dotenv

def geocode_addresses(addresses: List[str]) -> List[Location]:
    load_dotenv()
    GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
    print("\n\nInside geocode_addresses function")
    results = []
    for address in addresses:
        url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={GEOAPIFY_API_KEY}"
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            results.append(Location(address=address, lat=coords[1], lng=coords[0], uuid = generate_uuid()))
    print("\nCompleted function geocode_addresses")
    return results


def geocode_locations_service(locations): 
    load_dotenv()
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