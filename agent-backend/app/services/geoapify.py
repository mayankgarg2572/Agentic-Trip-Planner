from ast import Dict
import httpx
from typing import List
from app.models.schemas import GeoAPILocInput, Location, userSpecifiedLocation
from app.utils.helpers import generate_uuid
from app.core.config import GEOAPIFY_API_KEY

def set_url(address: GeoAPILocInput) -> str:
    print("\n\nInside set_url function")
    url = f"https://api.geoapify.com/v1/geocode/search?"
    try:
        if address.geocode_text:
            url+=f"text={address.geocode_text}"
        if address.city:
            url+=f"&city={address.city}"
        if address.state:
            url+=f"&state={address.state}"
        if address.country:
            url+=f"&country={address.country}"
        if address.postcode:
            url+=f"&postcode={address.postcode}"
        # if address.geocode_type and address.geocode_type != "unknown":
        #     url+=f"&type={address.geocode_type.value}"
        if address.name_canonical:
            url+=f"&name={address.name_canonical}"

    except Exception as e:
        print("Getting error for address:", address, "\nError is:", e)
        raise ValueError(f"Invalid address error:{e}")
    url+=f"&apiKey={GEOAPIFY_API_KEY}"
    return url


def geocode_addresses(address: GeoAPILocInput) -> Location | None:
    print("\n\nInside geocode_addresses function")
    
    data  = {}
    try:
        url = set_url(address)
        
        # print("final_url:", url)
        response = httpx.get(url)
        data = response.json()
        response.raise_for_status()
    except Exception as e:
        print("\nGetting error in extracting location coordi, for location:", address, "\nError is:", e)
        return None

    if data and data['features']:
        coords = data['features'][0]['geometry']['coordinates']
        return Location(address=address.name_canonical, lat=coords[1], lng=coords[0], uuid=generate_uuid())
    else:
        print("Not able to extract location coordi, for location:", address, "\nThe api(extract_location_coordinate) response was:", data)
        return None


def geocode_locations_service(locations: List[GeoAPILocInput]): 
    """
    This function accepts a list of location dictionaries with 'name' keys,
    and returns a list of Location objects with geocoded coordinates.
    Args:
        locations (List[dict]): A list of location dictionaries.
    
    Returns:
        List[Location]: A list of Location objects with geocoded coordinates.
    """

    print("\n\nInside geocode_locations_service function")
    geo_results = []    
    for loc in locations:
        loc_info = geocode_addresses(loc)
        if loc_info:
            geo_results.append(loc_info)
        else:
            print(f"Geocoding failed for location: {loc.name_canonical}")
            continue
    return geo_results

# Lets access the address of the locations specified by user using their coordinates
def reverse_geocode_coordinates(coords: List[userSpecifiedLocation]) -> List[Location]:
    print("\n\nInside reverse_geocode_coordinates function")
    results = []
    for coord in coords:
        lat = coord.lat
        lng = coord.lng
        url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lng}&apiKey={GEOAPIFY_API_KEY}"
        data  = {}
        try:
            response = httpx.get(url)
            data = response.json()
            response.raise_for_status()
        except Exception as e:
            print("Getting error in extracting location address, for coordinates:", coord, "\nError is:", e)
            continue

        if data and data['features']:
            address = data['features'][0]['properties']['formatted']
            results.append(Location(address=address, lat=lat, lng=lng, uuid = generate_uuid()))
        else:
            print("Not able to extract location address, for coordinates:", coord, "\nThe api(reverse_geocode_coordinates) response was:", data)
            continue
    return results


