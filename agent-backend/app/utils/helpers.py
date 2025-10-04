import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

def correct_final_llm_response_format(prompt:str, llm, final_llm_result:str) -> str:
    print("\n\nInside the correct_final_llm_response_format function")
    prompt = (
            "The previous response was not in the correct format. Please correct it. And you must only provide the response, no explanatory text or nothing else.\n\n"
            f"Previous response: {final_llm_result}\n\n"
            f"Correct format instructions: {prompt}\n\n"
            "Please provide the corrected response now(you have to only consider the format, and must not make any change in the response value and also do not provide any other explanatory text or context)."
        )
    try:
        content = llm.invoke(prompt)
        content = content.content if hasattr(content, "content") else str(content)
        return content
    except Exception as e:
        print("Error occurred while correcting the format:", e)
        raise e
