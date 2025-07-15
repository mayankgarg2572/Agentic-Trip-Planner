from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
web_search_tool = TavilySearchResults(k=3)



def web_search_service(query: str) -> List[str]:
    print("\n\nInside the web_search_service_function, with args:", query)
    docs = web_search_tool.invoke({"query": query})
    web_results = [d["content"] for d in docs]
    print("\nWeb_search_service response completed")
    return web_results

