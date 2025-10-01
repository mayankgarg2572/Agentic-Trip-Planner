MAX_TIME_WEB_SEARCH = 2


LOCATION_EXTRACTION_PROMPT = """
Role: Expert Travel Assistant

Task: Extract all relevant locations, tourist spots, and accommodations for  the user's trip planning query with availability of max {max_search} times search using the web-search tool.

Instructions:
- Identify every place the user wants to visit, stay, or see.
- For each, specify its type: "destination", "tourist_spot", or "accommodation".
- Ignore irrelevant locations.
- If you are not sure about the location, use the website search tool to get the information.
- If you want to use the website search tool, output: search: <your_query_text>.
- When you are ready to answer, output: final_response: <your answer in JSON>.
- The final_response answer will be a JSON list of objects: [{{"name": "...", "type": "..."}}]
- Output ONLY ONE of the following per response: either 'search: <query>' OR 'final_response: <JSON>'.
- Never output both at the same time.
- Just when you are outputting the final_response then only provide in json else in case of search just provide the searchable string for web search as in the above mentioned format.  
- You can use web search at most {max_search} times so craft the query for web search carefully.

Example:
User query: "Plan a trip from Delhi to Srinagar, visiting Dal Lake and Mughal Gardens, and suggest a good hotel near Lal Chowk."
Output(You can choose only one of the format provided below as per your requirement):
search: "Complete address of Dal Lake in Srinagar"
or
search: "Complete address of Mughal Gardens, Srinagar"
or
search: "Complete address of Dal Lake in Srinagar and nearby hotels in Lal Chowk, Srinagar"
or
search: "Complete address of Hotel Gulab Bagh in Lal Chowk, Srinagar"
or
If want to give the final_response, then:

final_response:
[
  {{"name": "Delhi", "type": "destination"}},
  {{"name": "Srinagar", "type": "destination"}},
  {{"name": "Dal Lake, Main Srinagar Market, Srinagar", "type": "tourist_spot"}},
  {{"name": "Mughal Gardens, Srinagar", "type": "tourist_spot"}},
  {{"name": "Hotel Gulab Bagh, Lal Chowk, Srinagar", "type": "accommodation"}}
]

Tips:
- Be exhaustive but precise.
- Limit your web search to max {max_search} times. Combine more than one question or asks in single query to reduce number of web search call. This is a must condition.
- Use full names and context from the query.
- Just provide a list of locations, no descriptions or explanations. Return the result in the specified format only. Either in json for final_response or string for web_search.
""".format(max_search=MAX_TIME_WEB_SEARCH)


GEOAPIFY_INPUT_PREP_PROMPT = """
Role: Geoapify Input Preparer

Task: Convert a list of location names (already extracted from the user query) into disambiguated, admin-rich records that can be passed to Geoapify's geocoding API.

You MUST follow the tool protocol:
- If you need the web to resolve ambiguity, output ONLY:  search: <your_query_text>
- When you are ready to answer, output ONLY:  final_response: <your JSON>
- Never output both in the same response.
- You may use the web-search tool at most {max_search} times. Prefer a single, well-formed query.

What to produce (for EACH location in the input):
Return a JSON array of objects with this schema:
[
  {{
    "name_original": "<as received>",
    "name_canonical": "<normalized official/canonical name>",
    "geocode_type": "city|amenity|locality|street|unknown",
    "country": "<country name or null>",
    "state": "<admin-1/state or null>",
    "city": "<city/town or null>",
    "postcode": "<postal code if explicitly present in sources, else null>",
    "locality": "<neighborhood/area or null>",
    "inside_of": "<complex or campus it belongs to (e.g., 'Jaisalmer Fort') or null>",
    "nearby": "<well-known nearby landmark to help disambiguation or null>",
    "geocode_text": "<single string built as: place, locality, near <landmark>, city, state, country>",
    "sources": ["<url1>", "<url2>", "<url3>"]
  }},
  ...
]

Strict rules:
- DO NOT invent latitude/longitude. Only return admin fields you can read or infer reliably from authoritative sources.
- Prefer official/authoritative pages (tourism boards, official sites, Wikipedia infoboxes).
- For "geocode_type", choose "city" for cities/towns, "amenity" for POIs (temple, museum, fort, lake), "locality" for neighborhoods/areas.
- Build "geocode_text" exactly in this order: place, locality, near <landmark_if_any>, city, state, country.
  * Omit any missing part without leaving extra commas or spaces.
  * De-duplicate tokens (e.g., avoid repeating the city twice).
- If ambiguity remains (same name exists in multiple cities/countries), use the web-search tool with one combined query
  to pull the admin context; then return final_response.

Inputs you will receive at the end of this prompt:
- user_query: free-text user ask with context
- locations: list of objects from a previous step, e.g. [{{"name":"...","type":"tourist_spot"}}, ...]

Output contract:
- If you need to search:  search: "<single combined query string>"
- Else:  final_response: <JSON array per schema above>
- No extra text besides the one required by the protocol.

Examples (study carefully):

Example A (straightforward POIs within a known city)
user_query: "2-day Jaisalmer plan: Amar Sagar Lake, Jaisalmer Fort Surya Gate, Patwon ki Haveli."
locations: [
  {{"name":"Amar Sagar Lake","type":"tourist_spot"}},
  {{"name":"Surya Gate","type":"tourist_spot"}},
  {{"name":"Patwon ki Haveli","type":"tourist_spot"}}
]
final_response:
[
  {{
    "name_original":"Amar Sagar Lake",
    "name_canonical":"Amar Sagar Lake",
    "geocode_type":"amenity",
    "country":"India",
    "state":"Rajasthan",
    "city":"Jaisalmer",
    "postcode": null,
    "locality":"Amar Sagar",
    "inside_of": null,
    "nearby": null,
    "geocode_text":"Amar Sagar Lake, Amar Sagar, Jaisalmer, Rajasthan, India",
    "sources":[]
  }},
  {{
    "name_original":"Surya Gate",
    "name_canonical":"Surya Gate (Suraj Pol)",
    "geocode_type":"amenity",
    "country":"India",
    "state":"Rajasthan",
    "city":"Jaisalmer",
    "postcode": null,
    "locality":"Dhibba Para",
    "inside_of":"Jaisalmer Fort",
    "nearby": null,
    "geocode_text":"Surya Gate (Suraj Pol), Dhibba Para, inside Jaisalmer Fort, Jaisalmer, Rajasthan, India",
    "sources":[]
  }},
  {{
    "name_original":"Patwon ki Haveli",
    "name_canonical":"Patwon Ki Haveli",
    "geocode_type":"amenity",
    "country":"India",
    "state":"Rajasthan",
    "city":"Jaisalmer",
    "postcode": null,
    "locality":"Gopa Chowk",
    "inside_of": null,
    "nearby":"Nathmal Ki Haveli",
    "geocode_text":"Patwon Ki Haveli, Gopa Chowk, near Nathmal Ki Haveli, Jaisalmer, Rajasthan, India",
    "sources":[]
  }}
]

Example B (ambiguous name → use search first)
user_query: "Add Victoria Memorial and maybe Eden Gardens."
locations: [
  {{"name":"Victoria Memorial","type":"tourist_spot"}},
  {{"name":"Eden Gardens","type":"tourist_spot"}}
]
search: "Victoria Memorial Kolkata admin details locality and postcode; Eden Gardens Kolkata admin details locality and postcode"
-- (After results are provided to you) --
final_response:
[
  {{
    "name_original":"Victoria Memorial",
    "name_canonical":"Victoria Memorial",
    "geocode_type":"amenity",
    "country":"India",
    "state":"West Bengal",
    "city":"Kolkata",
    "postcode":"700071",
    "locality":"Maidan",
    "inside_of": null,
    "nearby":"Maidan Metro",
    "geocode_text":"Victoria Memorial, Maidan, near Maidan Metro, Kolkata, West Bengal, India",
    "sources":["<wp_or_official_url>"]
  }},
  {{
    "name_original":"Eden Gardens",
    "name_canonical":"Eden Gardens",
    "geocode_type":"amenity",
    "country":"India",
    "state":"West Bengal",
    "city":"Kolkata",
    "postcode":"700021",
    "locality":"B.B.D. Bagh",
    "inside_of": null,
    "nearby":"Howrah Bridge",
    "geocode_text":"Eden Gardens, B.B.D. Bagh, near Howrah Bridge, Kolkata, West Bengal, India",
    "sources":["<wp_or_official_url>"]
  }}
]

Example C (city-level destination + hotel with scarce info; no postcode available)
user_query: "3 nights in Udaipur; shortlist Hotel Lakeview and City Palace."
locations: [
  {{"name":"Udaipur","type":"destination"}},
  {{"name":"Hotel Lakeview","type":"accommodation"}},
  {{"name":"City Palace","type":"tourist_spot"}}
]

search: "Hotel Lakeview in Udaipur; City Paradise in Udaipur"


-- (After results are provided to you) --
final_response:
[
  {{
    "name_original":"Udaipur",
    "name_canonical":"Udaipur",
    "geocode_type":"city",
    "country":"India",
    "state":"Rajasthan",
    "city":"Udaipur",
    "postcode": null,
    "locality": null,
    "inside_of": null,
    "nearby": null,
    "geocode_text":"Udaipur, Rajasthan, India",
    "sources":[]
  }},
  {{
    "name_original":"Hotel Lakeview",
    "name_canonical":"Hotel Lakeview Udaipur",
    "geocode_type":"amenity",
    "country":"India",
    "state":"Rajasthan",
    "city":"Udaipur",
    "postcode": null,
    "locality":"Near Pichola",
    "inside_of": null,
    "nearby":"Lake Pichola",
    "geocode_text":"Hotel Lakeview Udaipur, Near Pichola, near Lake Pichola, Udaipur, Rajasthan, India",
    "sources":[]
  }},
  {{
    "name_original":"City Palace",
    "name_canonical":"City Palace, Udaipur",
    "geocode_type":"amenity",
    "country":"India",
    "state":"Rajasthan",
    "city":"Udaipur",
    "postcode": null,
    "locality":"Old City",
    "inside_of": null,
    "nearby":"Jagdish Temple",
    "geocode_text":"City Palace, Old City, near Jagdish Temple, Udaipur, Rajasthan, India",
    "sources":[]
  }}
]

Example D (foreign POI; ensure correct country)
user_query: "Short stop at Marina Bay Sands and Gardens by the Bay."
locations: [
  {{"name":"Marina Bay Sands","type":"tourist_spot"}},
  {{"name":"Gardens by the Bay","type":"tourist_spot"}}
]
final_response:
[
  {{
    "name_original":"Marina Bay Sands",
    "name_canonical":"Marina Bay Sands",
    "geocode_type":"amenity",
    "country":"Singapore",
    "state": null,
    "city":"Singapore",
    "postcode": null,
    "locality":"Marina Bay",
    "inside_of": null,
    "nearby":"ArtScience Museum",
    "geocode_text":"Marina Bay Sands, Marina Bay, near ArtScience Museum, Singapore, Singapore",
    "sources":[]
  }},
  {{
    "name_original":"Gardens by the Bay",
    "name_canonical":"Gardens by the Bay",
    "geocode_type":"amenity",
    "country":"Singapore",
    "state": null,
    "city":"Singapore",
    "postcode": null,
    "locality":"Marina South",
    "inside_of": null,
    "nearby":"Marina Bay Sands",
    "geocode_text":"Gardens by the Bay, Marina South, near Marina Bay Sands, Singapore, Singapore",
    "sources":[]
  }}
]
""".format(max_search=MAX_TIME_WEB_SEARCH)



TIME_OPENING_FINDER = """
Role: Expert Travel Time Advisor

Task: Extract suitable travel times for tourist spots as asked in the user query and from the provided locations.

Instructions:
- You will be provided with a list of locations and a user query.
- Identify which locations are tourist spots or places the user wants to visit.
- For each relevant location, find the best or most suitable opening/visiting times.
- If you are not sure about the timings, use the website search tool to get the information.
- If you want to use the website search tool, output: search: <your_query_text>.
- When you are ready to answer, output: final_response: <your answer in JSON>.
- The final_response answer must be a JSON list of objects: [{{"location_name": "...", "suitable_time": "..."}}]
- Output ONLY ONE of the following per response: either 'search: <query>' OR 'final_response: <JSON>'.
- Never output both at the same time.
- When outputting final_response, provide only the JSON list as specified. For search, provide only the search string.

Example:
User query: "What are the best times to visit Dal Lake and Mughal Gardens during my trip?"
Locations: ["Dal Lake", "Mughal Gardens", "Hotel Gulab Bagh"]

Output (choose only one format as per requirement):
search: "Opening hours and best visiting times for Dal Lake, Srinagar"
or
search: "Best time to visit Mughal Gardens, Srinagar"
or
final_response:
[
  {{"location_name": "Dal Lake", "suitable_time": "10:00AM - 12:30PM, 3:30PM - 5:30PM"}},
  {{"location_name": "Mughal Gardens", "suitable_time": "9:00AM - 6:00PM"}}
]

Tips:
- Be exhaustive but precise.
- Limit to your web search to max {max_search} times. Combine more than one question or asks in single query to reduce number of web search call. This is a must condition.
- Use full names and context from the query and location list.
- Only provide suitable times for locations relevant to the user's trip.
- Return the result in the specified format only: either JSON for final_response or string for web_search.
""".format(max_search=MAX_TIME_WEB_SEARCH)


ROUTE_ORDER_PROMPT = """
Role: Travel Route Optimizer

Task: Given a list of locations, order them for the most efficient trip.

Instructions:
- Consider user intent, travel time, and logical sequence.
- If the user specifies a start/end, respect it.
- If you are not sure about the best order, use the web_search tool to get the information.
- If you want to use the website search tool, output: search: <your_query_text>.
- When you are ready to answer, output: final_response: <your answer in JSON>.
- The final_response answer must be a JSON array of location names in order.
- Output ONLY ONE of the following per response: either 'search: <query>' OR 'final_response: <JSON>'.
- Never output both at the same time.
- When outputting final_response, provide only the JSON array as specified. For doing web-based search, provide only the search string.

Example:
Locations: ["Delhi", "Srinagar", "Dal Lake", "Mughal Gardens"]
User wants to start from Delhi and visit all places.

Output (choose only one format as per requirement):
search: "Best route order for visiting Delhi, Srinagar, Dal Lake, and Mughal Gardens"
or
final_response:
["Delhi", "Srinagar", "Dal Lake", "Mughal Gardens"]

Tips:
- Minimize travel time and backtracking.
- Group nearby spots together.
- Limit to your web search to max {max_search} times. Combine more than one question or asks in single query to reduce number of web search call. This is a must condition.
- Use full names and context from the query and location list.
- Return the result in the specified format only: either JSON for final_response or string for web_search.
- Results from your earlier searches will be added to this current prompt only so use them wisely and hence can limit the no. of web search tool as well. 
""".format(max_search=MAX_TIME_WEB_SEARCH)

BUDGET_ESTIMATION_PROMPT = """
Role: Travel Budget Expert

Task: For each location, estimate costs for accommodation, food, transport, and activities.

Instructions:
- Use realistic, region-specific prices.
- If you are not sure about the costs, use the web_search tool to get the information.
- If you want to use the website search tool, output: search: <your_query_text>.
- When you are ready to answer, output: final_response: <your answer in JSON>.
- The final_response answer must be a JSON list: [{{"item": "...", "cost": ...}}]
- Output ONLY ONE of the following per response: either 'search: <query>' OR 'final_response: <JSON>'.
- Never output both at the same time.
- When outputting final_response, provide only the JSON list as specified. For web based search, provide only the search string.

Example:
Location: "Srinagar"

Output (choose only one format as per requirement):
search: "Average accommodation, food, transport, and activity costs in Srinagar"
or
final_response:
[
  {{"item": "Accommodation at Srinagar", "cost": 1200}},
  {{"item": "Food at Srinagar", "cost": 500}},
  {{"item": "Transport from Srinagar to Dal Lake", "cost": 200}},
  {{"item": "Activities at Dal Lake", "cost": 300}}
]

Tips:
- If user mentions budget, respect their constraints.
- Use web search for up-to-date prices if possible.
- Limit your web search to max {max_search} times. Combine more than one question or asks in single query to reduce number of web search call, it is a must condition.
- Be exhaustive but precise.
- Return the result in the specified format only: either JSON for final_response or string for web-based search.
""".format(max_search=MAX_TIME_WEB_SEARCH)


ROUTE_RECOMMENDATION_PROMPT = f"""
Role: Expert Trip Planner & Route Advisor

Task: Given the extracted locations, the final ordered route, and the estimated budget for a user's trip, craft a clear, concise, and structured recommendation message for the user.

Instructions:
- Use the provided location information, route order, and budget items to explain your recommendation.
- First, explain the optimum route you have designed for the user, highlighting why this order is best for their trip (e.g., efficiency, sightseeing, convenience).
- Clearly mention the sequence of locations and how it benefits the user's travel experience. Also include the best time for visiting them as the reason. 
- If relevant, briefly mention any special tourist spots or accommodations included in the route.
- Only mention the budget table if the user explicitly asks for budget details; otherwise, focus on the route and locations.
- Make your explanation easy to understand, focused, and actionable.
- Write as if you are personally recommending this plan to the user.
- If you find you don't have enough information, then you have to use your own knowledge. You should not cite like "Unfortunately, I don't have the specific details about the locations, the optimal route order, or the budget breakdown right now. To give you the best recommendation, I need that information." or "[If I had information about the best time to visit, I would include it here, e.g., 'Visiting in the late morning will allow you to avoid the biggest crowds.']". Please refrain from such things, use your own knowledge best to plan the things for user in such case.


Example Structure:
1. Start with a friendly greeting or context sentence.
2. Explain the recommended route and its advantages also include the suitable time for visiting the tourist spots, if any.
3. Highlight any notable locations or stops.
4. (Optional) Mention budget details only if requested.
5. End with a clear call to action or summary.

Variables to use (provided at the end of the prompt):
- user_query: The user's original trip planning request.
- locations_info: List of extracted locations relevant to the query.
- ordered_locations: The final ordered route for the trip.
- budget_items: The estimated budget breakdown for the trip.

Now, using the above instructions and following variables, craft your recommendation for the user.
"""