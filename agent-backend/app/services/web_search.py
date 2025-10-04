from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=3)

def llm_with_web_search(prompt, llm, max_loops=2):
    final_content = [""]
    print(f"Inside llm_with_web_search")
    for _ in range(max_loops+1):
        
        result = llm.invoke(prompt)
        
        content = result.content if hasattr(result, "content") else str(result)
        content = content.strip()
        if content.startswith("search:"):
            content = content.replace('"', '').replace("'", '')
            search_query = content[len("search:"):].strip()
            # also need to remove the things like " or ' or from the content
            search_results = web_search_service(search_query)
            final_content+=search_results
            if _ == max_loops -1 :
                prompt += f"\n\nWeb search results for '{search_query}': {search_results}\n\n\nNow, since this was your final query, now please craft the response for the asked task and the response must be in the specified format only."

            else:
                prompt += f"\n\nWeb search results for '{search_query}': {search_results}\nNow, based on this, continue."
        elif content.startswith("final_response:"):
            return content[len("final_response:"):].strip()
        else:
            return content
    print("Not able to complete the web search, too much calls, sample final content(max 3):", final_content[:min(len(final_content), 3)])
    return " ".join(final_content)



def web_search_service(query: str) -> List[str]:
    try:
        # Use the tool-call form to get a ToolMessage with .artifact["results"]
        msg = tool.invoke({
            "name": "tavily", "type": "tool_call", "id": "t1",
            "args": {"query": query}
        })
        # print(msg)
        results = getattr(msg, "artifact", {}).get("results", [])
        # print("Sample results from web search for query:", query, "\n\nResult:\n", results[:min(3, len(results))])
        return [r.get("content", "") for r in results]
    except Exception as e:
        print("Getting error:", e)
        return []

