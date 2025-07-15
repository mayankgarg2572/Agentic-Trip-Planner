# Getting Started

This project is a AI-Agetic Trip Planner built using React, NodeJS, and FastAPI. It allows users to plan trips with the help of AI agents, providing a seamless and interactive experience. This is not yet a complete project, but it is a work in progress.

The React UI is encompassing currently the interaction with the shown map. Users can search for the location and will see the result in left side panel. The right side panel is reserved for the AI agent interaction, which is not yet implemented. 

The NodeJS backend is functional and serves the GeoApify API for the searching operation in the React UI. It also saves whaterver the user searches in the mongoDB database. The NodeJS backend is currently running on port 5000.

The FastAPI backend is specifically for the Agentic implementation using LangGraph. I have planned it in the following way. Let me share with you what I have finally decided. 

Node 1 -> Tools : [web_search, geoapify_for_location_search, geoapify_for route_search] => It will extract all the things which are required by the user like the optimum route and the respective budget etc.. I will have a specific format for answer here. This will help me to show the respective UI interactionn over the map easil.y For e.g. If the user have asked to make a trip to some location from his current location. Then this node willl extract the locations' geopoint like the exact langitudes and latitudes using geoapify location search tool and then it will use the geoapify_route_search tool to get the optimum route from the current location to the destination location. It may then also use the web_search tool to get the budget for the trip and other things like the best time to visit that place, nearby tourist spots and their best time for visiting etc..  Here I will also extract the location of nearby tourist spots and accomodation using web search and geoapify_location_search that will help me to mark them better over my map UI highly interactive, informative and user friendly. For optimizing the route, I will use the geoapify_route_search tool which will give me the best route from the current location to the destination location. So if there are more than two location ing the route then I will first need to find shortest route from every location to every other location and then find the best complete routestarting from location A to every other location or what as recommended by the user.

Now let me cite the complete functionality of the Node 1:
1. It will take the user query as input.
2. It will use the `geoapify_for_location_search` tool to find the locations. This tool will return the locations' geopoint like the exact latitudes and longitudes and the full address of the location in words like, "Nehru Udhyaan, Laal Chowk, Srinagar, Jammu and Kashmir, India".
3. It will use the `geoapify_for_route_search` tool to find the best route from a location A to the location B. It will only accept two locations at a time.
4. It will use the `web_search` tool to find the budget for the trip and other things like the best time to visit that place, nearby tourist spots and their best time for visiting, accomodation, food, transport etc.
5. It will extract the locations of nearby tourist spots and accomodation using web search and geoapify_location_search that will help me to mark them better over my map UI highly interactive, informative and user friendly.
6. It will craft the budget for the respective trip in a specific format which will be used to show as the budget table over the UI.
7. It will return the final response in a specific format which will be used to show the respective UI interaction over the map easily.


Now let me cite the order of execution for different user requirements in the Node 1:

1. It will first check all the user requirements like is the user interested in finding the best route also, is the user interested in finding the nearby accommodation or nearby tourist spots for a location, if the user is interested in optimizing its route, if the user is interested in budget estimation.

2. Now it will do a web search for only things like best accomodation nearby a location, best tourist spot nearby a location, and the best time to visit the respective tourist locations which may be required for optimizing the route.

3. Now after finding all the basic word like addresss of all the locations, accomodations and their tourist spots from the web search, it will use the `geoapify_for_location_search` tool to find the exact geopoint of all the locations, accomodations and tourist spots.

4. Now it will use the `geoapify_for_route_search` tool to do the route estimation for every location to every other location. For the tourist location location near by some major location then it will just search for the route specific to those nearby tourist spot and the major location. For e.g. the user will be visiting Srinagar and he wants to visit the nearby tourist spots like Dal Lake, Mughal Gardens, etc. So it will first find the route from the current location to Srinagar and then it will find the route from Srinagar to Dal Lake and then from Dal Lake to Mughal Gardens and so on, and then order them in a way that the route is optimized and the user can visit all the tourist spots in the best possible way. Now if the user is visiting more than one such major location and interested in visiting nearby tourist spots for each location then it will find the route from the current location to the first major location and then from the first major location to the second major location and so on. And also it will find the route for all the tourist locations from major Location A and simiarly for major location B and so on. So it is like an iterative process. For  each location and its tourist spots I might need to optimize them as a single route. similarly for the next major location and its tourist spots I might need to optimize them as a single route. And then I will optimize the route for all major locations so the user can visit all the tourist spots in the best possible way.

5. Now it will use the `web_search` tool to find the budget for the trip including accomodation, food, transport, entry fees etc. as applicable. 

6. Now it will correctly format all the information extracted above in the specific format as mentioned earlier. 



Node 2 -> It will verify the result generated by the Node 1 to check if it is following the user requirement or not and is not hallucinated(not accurate) and  if it finds the response okay it will end otherwise it may fallback to the Node 1 again. It can make max 2 fallback to Node 1. If it still find the response not okay then it will end the process with whatever generated final response.

The respective structure of the response which I am expecting from the Node 1 is as follows:

```json
{
    "location_to_mark_on_ui": [Location()],
    "location_order_for_showing_route_on_ui": [location_ids...],
    "chat_response": "",
    "budget_table": {
        "total_budget": 0,
        "budget_breakdown": [
            {
                "item": "Accommodation at Location A",
                "cost": 0
            },
            {
                "item": "Food at Location A",
                "cost": 0
            },
            {
                "item": "Transport from Location A to Location B",
                "cost": 0
            },
            {
                "item": "Activities at Location A",
                "cost": 0
            }
        ]
    }
}
```
Here `location_to_mark_on_ui` is an array of `Location` objects that will be marked on the map UI. This will contain all the location like any accomodations, nearby tourists places etc.. which are required or asked by the user.

Each `Location` object contains the id, name, latitude, and longitude of the location.
Here the Location() is a class which will have the following attributes:

```python
class Location:
    def __init__(self, name: str, latitude: float, longitude: float):
        self.id = str(uuid.uuid4())  # Unique identifier for the location
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
```

Here name is the full address of the location in words like, "Nehru Udhyaan, Laal Chowk, Srinagar, Jammu and Kashmir, India" and latitude and longitude are the respective coordinates of the location.

In the `location_order_for_showing_route_on_ui` array, I will have the ids of the locations in the order they should be shown on the map for the route.

Now in this case what will be my Agent's state class should contain? 

```python
class AgentState:
    def __init__(self):
        self.user_query = ""
        self.location_to_mark_on_ui = [Location()]  # List of Location objects
        self.location_order_for_showing_route_on_ui = [location_ids...]  # List of location ids
        self.chat_response = ""  # Response to be shown in the chat UI
        self.budget_table = {
            "total_budget": 0,
            "budget_breakdown": [BudgetElement()]  # List of budget items
        }
```

Now the `BudgetElement` class will have the following attributes:

```python
class BudgetElement:
    def __init__(self, item: str, cost: float):
        self.item = item  # Description of the budget item
        self.cost = cost  # Cost of the budget item
```

I haven't yet implemented it. I was getting everytime confused for the Agent's graph structure, as I was trying to decentralize the node 1 more and more but everytime it was getting more and more complex and difficult to handle. So I have finally decided to keep it simple and have only two nodes for now.

---

## Available Scripts


Currently the React UI is working and the NodeJS backend is functional. The FastAPI backend is not yet implemented.

So after cloning the repo, you can run the following commands to start the project:
1. **Install dependencies for React UI**:
```bash
cd frontend
npm install
```

2. **Setup the Node.js Backend**:
    - Create a `.env` file in the `backend` directory by compaying content from your .env.test in the same backend folder. Then add your corresponding MongoDB URI, GeoApify API key, and OpenAI API key.

    - Install dependencies:

```bash
cd backend
npm install
```

3. **Start the Node.js Backend**:

```bash
npm run dev
```

4. **Start the React UI**:
```bash
cd frontend
npm start
```



---


