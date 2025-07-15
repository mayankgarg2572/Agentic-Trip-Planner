import uuid
from app.models.schemas import Location, BudgetElement
from app.services.geoapify import geoapify_for_location_search, geoapify_for_route_search
from app.services.web_search import web_search
from app.new_agent.pipeline import llm_extract_locations, llm_order_locations, llm_estimate_budget

class ExtractionGenerationNode:
    def __call__(self, state):
        # user_query = state.user_query

        # # Step 1: Extract locations/entities from user query using LLM
        # locations_info = llm_extract_locations(
        #     user_query,
        #     prompt="""Extract all locations, tourist spots, and accommodations mentioned or implied in the following trip planning query. 
        #     Return a list of names and types (destination, tourist spot, accommodation). Query: {query}"""
        # )

        # # Step 2: Geocode locations using Geoapify
        # locations = []
        # for loc in locations_info:
        #     geo_result = geoapify_for_location_search(loc['name'])
        #     if geo_result:
        #         locations.append(
        #             Location(
        #                 id=str(uuid.uuid4()),
        #                 name=geo_result['address'],
        #                 latitude=geo_result['lat'],
        #                 longitude=geo_result['lng']
        #             )
        #         )

        # # Step 3: Order locations for route optimization using LLM
        # ordered_names = llm_order_locations(
        #     [loc.name for loc in locations],
        #     prompt="""Given these locations, order them for an optimal trip route based on typical travel logic and user intent. 
        #     Locations: {locations}"""
        # )
        # location_order = [loc.id for loc in locations if loc.name in ordered_names]

        # # Step 4: Get routes between consecutive locations using Geoapify
        # routes = []
        # for i in range(len(location_order) - 1):
        #     loc_a = next(loc for loc in locations if loc.id == location_order[i])
        #     loc_b = next(loc for loc in locations if loc.id == location_order[i+1])
        #     route = geoapify_for_route_search(loc_a.latitude, loc_a.longitude, loc_b.latitude, loc_b.longitude)
        #     routes.append(route)

        # # Step 5: Estimate budget items using LLM and web_search
        # budget_items = []
        # total_budget = 0
        # for loc in locations:
        #     budget_suggestions = llm_estimate_budget(
        #         user_query,
        #         loc.name,
        #         prompt=f"""For the location '{loc.name}', estimate budget items for accommodation, food, transport, and activities. 
        #         Return a list of item descriptions."""
        #     )
        #     for item in budget_suggestions:
        #         cost = web_search(item, loc.name)  # You can refine this to use more specific queries
        #         budget_items.append(BudgetElement(item=item, cost=cost))
        #         total_budget += cost

        # # Step 6: Craft chat response
        # chat_response = (
        #     f"Trip planned for: {', '.join([loc.name for loc in locations])}. "
        #     f"Total budget: {total_budget}."
        # )

        # # Step 7: Format state for UI
        # state.location_to_mark_on_ui = locations
        # state.location_order_for_showing_route_on_ui = location_order
        # state.chat_response = chat_response
        # state.budget_table = {
        #     "total_budget": total_budget,
        #     "budget_breakdown": [be.__dict__ for be in budget_items]
        # }
        user_query = state.get("user_query", "")
        from app.new_agent.pipeline import node1_pipeline
        response = node1_pipeline(user_query)
        state.update(response)
        return state
from app.utils.llm import MAIN_LLM
class VerificationNode:
    def __call__(self, state):
        """
        Node 2: Verify the result from Node 1, set state.verified accordingly.
        """
        # 1. Check if response matches user requirements and is not hallucinated
        # For demo, just check if locations and budget are present
        prompt = f"You are a response verifier from another agent. You have to just comment over the response geenrated for the user query. You have to carefully examine the solution and return just one word out of the two as 'verified' or 'not verified'. You will be provided with a object which will include all the information like the user query and the different informations generated as for example `location_order_for_showing_route_on_ui` which are in turn of helping the user to show the location visiting order for the user over the frontend UI. You don't have to judge accurately, You have to check just whether the information provided when presented in some correct format over the UI will be able to help the user or not. Here is that object:{state}"

        response  =  MAIN_LLM.invoke(prompt)
        print(response)
        # verified = bool(state.get("location_to_mark_on_ui")) and bool(state.get("budget_table", {}).get("total_budget", 0))
        state["verified"] = response
        # Optionally, add feedback
        if response == "not verified":
            state["feedback"] = "Missing locations or budget information."
        else:
            state["feedback"] = "Response verified."
        return state