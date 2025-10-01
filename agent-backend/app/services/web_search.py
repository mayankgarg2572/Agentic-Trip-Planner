from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=3)

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

