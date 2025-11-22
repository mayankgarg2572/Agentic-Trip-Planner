from typing import List
from langchain_community.tools.tavily_search import TavilySearchResults
from langsmith import traceable
import json
from app.utils.clean_load_json import remove_json_prefix_list
from app.utils.helpers import correct_final_llm_response_format
tool = TavilySearchResults(max_results=3)



def web_search_service(query: str) -> List[str]:
    try:
        msg = tool.invoke({
            "name": "tavily", "type": "tool_call", "id": "t1",
            "args": {"query": query}
        })
        results = getattr(msg, "artifact", {}).get("results", [])
        return [r.get("content", "") for r in results]
    except Exception as e:
        print("Getting error:", e)
        return []


def remove_prefix_markdown(content: str) -> str:
    if isinstance(content, str):
        content = content.strip()
        if content.startswith("```json"):
            content = content[len("```json"):].strip()
        if content.startswith("```"):
            content = content[len("```"):].strip()
        if content.endswith("```"):
            content = content[:-len("```")].strip()
    
    return content


def get_formatted_search_prompt(query, results, is_last_loop):
    """Helper to construct the follow-up prompt based on search results."""
    tmp_prompt = f"\n\nWeb search results for '{query}': {results}"
    
    if is_last_loop:
        tmp_prompt += "\n\n\nNow, since this is my final query to you, please craft the final response only for the asked task(not refine_request or search) and the response must be in the specified format only."
    else:
        tmp_prompt += f"\nNow, based on this, continue."
    
    return tmp_prompt


def handle_search_command(content:str, current_loop:int, max_loops:int):
    """Handles the 'search:' command logic."""
    # Clean content
    cleaned_content = content.replace('"', '').replace("'", '')
    search_query = cleaned_content[len("search:"):].strip()
    
    # Execute search
    search_results = web_search_service(search_query)
    
    # Create next prompt
    is_last_loop = (current_loop == max_loops-1)
    next_prompt_addition = get_formatted_search_prompt(search_query, search_results, is_last_loop)
    
    return search_results, next_prompt_addition


def handle_refine_command(content:str, current_prompt:str, current_loop:int, max_loops:int):
    """Handles the 'refine_request:' command logic."""
    payload = content[len("refine_request:"):].strip()
    req = json.loads(payload)
    
    search_query = req.get("new_search_query_to_use", "").strip()
    bullets = req.get("search_summary_current", [])
    print(current_loop, max_loops)
    # Update the base prompt with the summary
    updated_base_prompt = current_prompt + f"\n\nWeb search results for query:'{search_query}' is:\n- " + "\n- ".join(bullets) + f"\nNow, based on this, continue. current web search call turn count:{current_loop+1}"

    # Execute search
    search_results = web_search_service(search_query)
    
    # Create next prompt
    is_last_loop = (current_loop == max_loops-1)
    next_prompt_addition = get_formatted_search_prompt(search_query, search_results, is_last_loop)

    return updated_base_prompt, search_results, next_prompt_addition



@traceable
def llm_with_web_search(prompt, llm, max_loops=2):
    final_content_accumulator = [""]
    tmp_prompt = ""
    print(f"Inside llm_with_web_search")

    try:
        # We use max_loops + 1 to ensure there is an iteration for the final answer
        for i in range(0, max_loops + 1):

            result = llm.invoke(prompt + tmp_prompt)
            content = result.content if hasattr(result, "content") else str(result)
            content = remove_prefix_markdown(content)
            valid_step_complete = False
            print("i, max_loops:", i, max_loops)
            format_correction_count = 0
            while isinstance(content, str) and content != "" and format_correction_count<3:

                if content.startswith("search:"):
                    search_res, prompt_add = handle_search_command(content, i, max_loops)
                    final_content_accumulator.append( prompt_add)
                    tmp_prompt = prompt_add
                    valid_step_complete = True
                    break 

                elif content.startswith("final_response:"):
                    return content[len("final_response:"):].strip()

                elif content.startswith("refine_request:"):
                    prompt, search_res, prompt_add = handle_refine_command(content, prompt, i, max_loops)
                    final_content_accumulator.append(prompt_add)
                    tmp_prompt = prompt_add
                    valid_step_complete = True
                    break

                else:
                    print("Format invalid, attempting correction...")
                    result = correct_final_llm_response_format(prompt, llm, content)
                    content = remove_prefix_markdown(result)
                    format_correction_count+=1
            
            if valid_step_complete:
                continue
            else:
                print("Not able to format the LLM response in the required format:",content )

    except Exception as e:
        print("Error occurred in web search:", e)

    # Fallback if loop finishes or errors occur
    print("Not able to complete the web search, sample final content:", final_content_accumulator[:min(len(final_content_accumulator), 3)])
    return " ".join(final_content_accumulator)

