import httpx
from typing import List
from app.models.schemas import Location
from app.core.config import GEOAPIFY_API_KEY

def geocode_addresses(addresses: List[str]) -> List[Location]:
    results = []
    for address in addresses:
        url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={GEOAPIFY_API_KEY}"
        response = httpx.get(url)
        response.raise_for_status()
        data = response.json()

        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            results.append(Location(address=address, lat=coords[1], lng=coords[0]))
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


    addresses = [loc['name'] for loc in locations]
    geo_results = geocode_addresses(addresses)
    location_objs = []
    for loc, geo in zip(locations, geo_results):
        location_objs.append(
            Location(
                address=geo.address,
                lat=geo.lat,
                lng=geo.lng
            )
        )
    return location_objs