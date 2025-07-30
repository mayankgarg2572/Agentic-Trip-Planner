# Trip Planner AI — Agentic Trip Planning Platform

An AI‑Agentic Trip Planner built with **React**, **NodeJS**, and **FastAPI**.  
Users can search destinations, view map-based results, and interact with an AI travel assistant to plan optimal routes, estimate budgets, and discover accommodations and tourist spots.

---

## Table of Contents
1. [Features](#features)
2. [Architecture Overview](#architecture-overview)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [Project Structure](#project-structure)
6. [Usage Flow & Agent Design](#usage-flow--agent-design)
7. [Output Format & Agent State Design](#output-format--agent-state-design)
8. [License](#license)

---

## Features
- Interactive **React UI** with map search and dual‑panel layout  
- **NodeJS backend** serving GeoApify API and persisting searches to MongoDB  
- **FastAPI backend** implementing LangGraph agentic logic for travel planning  
- Automatic extraction of geolocations, optimized routing, budgets, tourist spots, and accommodations

---

## Architecture Overview

| Component     | Responsibility                                   | Key Tools                                 |
|---------------|--------------------------------------------------|--------------------------------------------|
| React UI      | Map + search interface, agent chat panel         | React, GeoApify JS client                  |
| NodeJS Server | Location lookup + data persistence               | Express, MongoDB, GeoApify API             |
| FastAPI Agent | Agentic processing for trip planning logic       | FastAPI, LangGraph, Python tools           |

---

## Installation & Setup

### Prerequisites
Version of tech stacks with which this project is built with
- Python: 3.10.0 for FastAPI agent  
- Node.js: v22.17.0
- MongoDB account / connection URI  
- GeoApify API key  
- Gemini API key: Setup at least 3 Gemini API Keys(in case using Free Tier API Key) for the Agent to work without any issue as there is limit for no. of call to LLM per minute which can limit our agent. Since we are using Thread safe Rotating Gemin API key Model which will rotate API key in case one API key exhausted its limit. 


### Step-by‑Step Setup

#### 1. Clone the repository
```bash
git clone <repo-url>
cd Trip_Planner_AI
```

#### 2. NodeJS Backend
```bash
cd backend
cp .env.test .env
# Edit .env: add MongoDB URI, GeoApify API key
npm install
```

#### 3. React Frontend
```bash
cd ../frontend
npm install
```

#### 4. FastAPI Agent Backend
```bash
cd ../agent-backend
python -m venv agentenv
cp .env.test .env # Setup at least 3 Gemini API Keys(in case using Free Tier API Key) for the Agent to work without any issue as there is limit for no. of call to LLM per minute which can limit our agent
agentenv/Scripts/activate
pip install -r requirements.txt
```

## Quick Start
Open 3 terminals inside the folder `Trip_Planner_AI` 

1. Launch backend (NodeJS) on first terminal
```bash
cd backend
npm run dev
```

2. Launch frontend on second terminal
```bash
cd ../frontend
npm start
```

3. Launch FastAPI agent API on port 8000
```bash
cd ../agent-backend
agentenv/Scripts/activate
python -m uvicorn app.main:app --reload
```

4. Interact via React UI: search location, chat with the agent


## Project Structure
```text
Directory structure:
├── README.md
├── test_trips.txt
├── agent-backend/
│   ├── .env.test
│   ├── app/
│   │   ├── main.py
│   │   ├── agent/
│   │   │   ├── graph.py
│   │   │   ├── nodes.py
│   │   │   ├── output_parser.py
│   │   │   ├── pipeline.py
│   │   │   └── prompts.py
│   │   ├── api/
│   │   │   ├── api_v1.py
│   │   │   └── endpoints/
│   │   │       └── agent.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── database.py
│   │   │   ├── directions.py
│   │   │   ├── geoapify.py
│   │   │   └── web_search.py
│   │   └── utils/
│   │       ├── helpers.py
│   │       ├── llm.py
│   │       └── rate_limiter.py
│   └── tests/
│       ├── test_agent.py
│       └── test_routes.py
├── backend/
│   ├── index.js
│   ├── package.json
│   ├── .env.test
│   ├── config/
│   │   └── db.js
│   ├── controllers/
│   │   └── locationController.js
│   ├── models/
│   │   └── Location.js
│   ├── routes/
│   │   └── locationRoutes.js
│   └── services/
│       └── mapService.js
└── frontend/
    ├── package.json
    ├── public/
    │   ├── index.html
    │   ├── manifest.json
    │   └── robots.txt
    └── src/
        ├── App.jsx
        ├── App.test.js
        ├── index.css
        ├── index.js
        ├── reportWebVitals.js
        ├── setupTests.js
        ├── api/
        │   └── api.js
        ├── components/
        │   ├── ChatAgent.jsx
        │   ├── ChatAgent.module.css
        │   ├── CustomSearchBar.jsx
        │   ├── CustomSearchBar.module.css
        │   ├── MapView.jsx
        │   ├── ResultsSidebar.jsx
        │   └── SearchBar.jsx
        ├── context/
        │   └── MapContext.jsx
        ├── pages/
        │   ├── Home.jsx
        │   └── Home.module.css
        ├── styles/
        │   └── App.css
        └── utils/
            └── mapUtils.js
```


## Usage Flow & Agent Design
- ### Node 1:

- Tools used: web_search, geoapify_for_location_search, geoapify_for_route_search

- Extracts exact coordinates, computes routes, gathers budgets, tourist spots, accommodations

- Optimizes multi-stop travel itinerary iteratively

- ### Node 2:

- Validates Node 1’s output against user requirements

- If inconsistencies or hallucinations exist, retries Node 1 up to two times

- Finalizes the output for UI consumption

## Output Format & Agent State Design

### Output Format from Node 1:
```json
{
  "location_to_mark_on_ui": [Location()],
  "location_order_for_showing_route_on_ui": [location_ids...],
  "chat_response": "",
  "budget_table": {
    "total_budget": 0,
    "budget_breakdown": [
      {"item": "Accommodation at Location A", "cost": 0},
      {"item": "Food at Location A", "cost": 0},
      {"item": "Transport from Location A to Location B", "cost": 0},
      {"item": "Activities at Location A", "cost": 0}
    ]
  }
}
```
- `Location` objects include: `id`, `name` (full address), `latitude`, `longitude`

- `location_order_for_showing_route_on_ui`: route sequence of location IDs

- `chat_response` : textual reply for chat UI

- `budget_table`: total cost and itemized breakdown


### Agent State Definition
```python
class AgentState:
    def __init__(self):
        self.user_query = ""
        self.location_to_mark_on_ui = []             # List[Location]
        self.location_order_for_showing_route_on_ui = []  # List[location_id]
        self.chat_response = ""
        self.budget_table = {
            "total_budget": 0.0,
            "budget_breakdown": []  # List[BudgetElement]
        }

class BudgetElement:
    def __init__(self, item: str, cost: float):
        self.item = item
        self.cost = cost
```

## License
(IIT Kharagpur License)

### Thank you for exploring Trip Planner AI.