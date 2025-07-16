class ExtractionGenerationNode:
    def __call__(self, state):
        user_query = state.get("user_query", "")
        from app.agent.pipeline import node1_pipeline
        response = node1_pipeline(user_query)
        state.update(response)
        return state


from app.utils.llm import MAIN_LLM
class VerificationNode:
    def __call__(self, state):
        """
        Node 2: Verify the result from Node 1, set state.verified accordingly.
        """
        prompt = f"You are a response verifier from another agent. You have to just comment over the response generated for the user query. You have to carefully examine the solution and return just one word out of the two as 'verified' or 'not verified'. You will be provided with a object which will include all the information like the user query and the different informations generated as for example `location_order_for_showing_route_on_ui` which are in turn of helping the user to show the location visiting order for the user over the frontend UI. You don't have to judge accurately, You have to check just whether the information provided when presented in some correct format over the UI will be able to help the user or not. It may be possible that some information is not able to generated, it's fine. You mainly have to check the friendlyness of the answer and the format of the response is a plausible format. Here is that object:{state}"

        print("\n\nInside the node 2")
        response  =  MAIN_LLM.invoke(prompt)
        
        if response.content == "not verified":
            state["verified"] = False
            state['fallback_count']+=1
        else:
            state["verified"] = True
        print("\nCompleted Node 2")
        return state