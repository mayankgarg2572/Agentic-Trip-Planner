from ast import Dict
import httpx
from typing import List
from app.models.schemas import GeoAPILocInput, Location, userSpecifiedLocation
from app.utils.helpers import generate_uuid
from app.core.config import GEOAPIFY_API_KEY
from langsmith import traceable
import time
from urllib.parse import urlencode

VALID_GEOCODE_TYPES = ["city", "country", "street", "postcode", "amenity", "locality"]

COUNTRY_CODES ={
    "india": "in",
    "unitedstates": "us",
    "unitedkingdom": "gb"
}

def build_structured_query_url(address:GeoAPILocInput) -> str:
    base = "https://api.geoapify.com/v1/geocode/search?"
    params  = {}
    try:
        if address.name_canonical and address.name_canonical != None:
            if address.name_canonical == address.city:
                params["name"]=address.name_canonical+" Airport"
            else:
                params["name"]=address.name_canonical
        if address.city and address.city != None:
            params["city"] =  address.city
        if address.state and address.state != None:
            params["state"]=address.state
        if address.country and address.country != None and COUNTRY_CODES[address.country.strip().lower()]:
            params["filter"]=f"countrycode:{COUNTRY_CODES[address.country.strip().lower()]}"
        if address.postcode and address.postcode != None:
            params["postcode"]=address.postcode
        if address.geocode_type and address.geocode_type.value in VALID_GEOCODE_TYPES:
            params["type"]=address.geocode_type.value
        params["limit"] = 1
        params["format"] = "json"
        params["apiKey"] = GEOAPIFY_API_KEY

        # URL encode properly
        url = base + urlencode(params)
        print(url)
    except Exception as e:
        print("Formatting error for address:", address, "\nError is:", e)
        raise ValueError(f"Invalid address error:{e}")
    return url


def build_unstructured_query_url(address:GeoAPILocInput) -> str:
    base = "https://api.geoapify.com/v1/geocode/search?"
    params  = {}
    try:
        if address.geocode_text:
            params["text"] = address.geocode_text
        if address.geocode_type and address.geocode_type.value != "unknown":
            params["type"]=address.geocode_type.value
        params["limit"] = 1
        params["format"] = "json"
        params["apiKey"] = GEOAPIFY_API_KEY
        url = base + urlencode(params)
    except Exception as e:
        print("Formatting error for address:", address, "\nError is:", e)
        raise ValueError(f"Invalid address error:{e}")
    return url

@traceable
def call_geoapify(url:str) -> List | None:
    data  = {}
    coords = []
    response: httpx.Response | None = None
    for attempt in range(3):
        try:
            response = httpx.get(
                url,
                timeout=httpx.Timeout(10.0, read=25.0)
            )
        except httpx.ReadTimeout:
            if attempt == 2: raise
            time.sleep(0.5 * (2 ** attempt))  # 0.5s, 1s backoff
        except Exception as e:
            print("\nGetting error in extracting location coordi, for location:", str(url), "\nError is:", e)
        # if response is None:
        #     raise httpx.ReadTimeout("No response after retries")    # make assignment guaranteed
        if response is not None:
            response.raise_for_status()  # check status before reading body
            data = response.json()
            if data and (('features' in data and data['features']) or( 'results' in data and data['results'])):
                break
    # Geoapify may return 'features' (GeoJSON) or 'results'
    if data:
        if 'features' in data and data['features']:
            coords = data['features'][0]['geometry']['coordinates']
        elif 'results' in data and data['results']:
            coords = [data['results'][0]['lon'],data['results'][0]['lat']]
        else:
            coords = None
    return coords



def geocode_addresses(address: GeoAPILocInput) -> Location | None:
    print("\n\nInside geocode_addresses function")
    url:str =""
    try:
        url = build_structured_query_url(address)
        coords = call_geoapify(url)
        if coords:
            return Location(address=address.name_canonical, lat=coords[1], lng=coords[0], uuid=generate_uuid())
    except Exception as e:
        print("Getting Exception for geoapify structured query call:", e)
    
    try:
        url = build_unstructured_query_url(address)
        coords = call_geoapify(url)
        if coords:
            return Location(address=address.name_canonical, lat=coords[1], lng=coords[0], uuid=generate_uuid())
    except Exception as e:
        print("Getting Exception for geoapify unstructured query call:", e)
    
    return None

@traceable
def geocode_locations_service(locations: List[GeoAPILocInput]): 
    print("\n\nInside geocode_locations_service function")
    if len(locations) == 0:
        print("No locations to geocode.")
        return []
    geo_results = []    
    for loc in locations:
        loc_info = geocode_addresses(loc)
        if loc_info:
            geo_results.append(loc_info)
        else:
            print(f"Geocoding failed for location: {loc.name_canonical}")
            continue
    return geo_results


@traceable
def reverse_geocode_coordinates(coords: List[userSpecifiedLocation]) -> List[Location]:
    print("\n\nInside reverse_geocode_coordinates function")
    if len(coords) == 0:
        print("No coordinates to reverse geocode.")
        return []
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

