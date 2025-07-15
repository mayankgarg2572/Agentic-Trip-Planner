from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
web_search_tool = TavilySearchResults(k=3)



def web_search_service(query: str) -> List[str]:
    # Placeholder implementation (replace with real API integration)
    
    docs = web_search_tool.invoke({"query": query})
    web_results = "\n\n".join([d["content"] for d in docs])
    # web_results = Document(page_content=web_results)

    return web_results

