# %%
import json
import os
from dotenv import load_dotenv
import os


from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# %%

# os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Load environment variables from .env file
load_dotenv()

# %%
os.environ["GOOGLE_API_KEY"] = os.getenv("MG2001_GOOGLE_API_KEY")

# %%
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0)

# %%
message = [
    SystemMessage(content="You are a friendly helper."),
    HumanMessage(content="What is my name?")
]

llm.invoke(message)

# %%
agent_memory=  {"human": "Name: Bob"}

system_prompt = "You are a chatbot. " \
+ "You have a section of your context called [MEMORY] " \
+ "which contains information relevant to your conversation with the user. "

message[0] = SystemMessage(
    content=system_prompt + "\n\n" + "MEMORY: " + json.dumps(agent_memory)
)

response = llm.invoke(message)

print(response.content)

# %% [markdown]
# ## Section 2: Modifying the Agent's memory with the help of a tool

# %%
agent_memory = {"human": "", "interaction_context_till_now":"", "agent":"" }

# def update_core_agent_memory(section: str, updated_memory: str):
#     """
#     {
#       "type": "function",
#       "name": "update_core_agent_memory",
#       "description": "Update the important information about the human, the agent, or the interaction context so far (summarized for minimal space).",
#       "parameters": {
#         "type": "object",
#         "properties": {
#           "section": {
#             "type": "string",
#             "enum": ["human", "interaction_context_till_now", "agent"],
#             "description": "Which memory section to update: 'human' (info about the human), 'interaction_context_till_now' (a concise summary of prior conversation), or 'agent' (info about yourself)."
#           },
#           "updated_memory": {
#             "type": "string",
#             "description": "The new memory content for the specified section; should be concise and relevant."
#           }
#         },
#         "required": ["section", "updated_memory"]
#       }
#     }
#     """
#     global agent_memory
#     if section in agent_memory:
#         agent_memory[section] = updated_memory
#     else:
#         raise ValueError(f"Section '{section}' does not exist in agent memory.")

def update_core_agent_memory(section: str, updated_memory: str):
    """
    Update the important information about you(the agent), or the whatever interaction context you have with the user or about the human you are interacting with. Here for the interaction context, you can save the main context of all the previous talks held till now(having higher proportions of recent talks) in most summarized phrase form which is easy to understand or recall and get stored in minimal space, so that you can use it in the future to recall the context of the conversation without having to go through all the previous messages.
    
    Args:
        section (str): Which memory section to update: 'human' (info about the human you are interacting with), 'interaction_context_till_now' (a concise summary of prior conversation), or 'agent' (info about yourself).
        updated_memory (str): The new memory content for the specified section; should be concise and relevant.
    
    
    """
    # """
    # {
    #   "type": "function",
    #   "name": "update_core_agent_memory",
    #   "description": "Update the important information about the human, the agent, or the interaction context so far (summarized for minimal space).",
    #   "parameters": {
    #     "type": "object",
    #     "properties": {
    #       "section": {
    #         "type": "string",
    #         "enum": ["human", "interaction_context_till_now", "agent"],
    #         "description": "Which memory section to update: 'human' (info about the human), 'interaction_context_till_now' (a concise summary of prior conversation), or 'agent' (info about yourself)."
    #       },
    #       "updated_memory": {
    #         "type": "string",
    #         "description": "The new memory content for the specified section; should be concise and relevant."
    #       }
    #     },
    #     "required": ["section", "updated_memory"]
    #   }
    # }
    # """
    global agent_memory
    if section in agent_memory:
        agent_memory[section] = updated_memory
    else:
        raise ValueError(f"Section '{section}' does not exist in agent memory.")





# %%
#Example usages
print("Initial Agent Memory:", agent_memory)
update_core_agent_memory("human", "Name: Alice")
print("Updated Agent Memory:", agent_memory)


# %%
tools = [
    update_core_agent_memory,
]

agent_memory = {"human": "", "interaction_context_till_now":"", "agent":"" }

system_prompt = "You are a helpful chatbot who always replies to user queries. And uses functional call only when necessary." \
+ "You have a section of your context called [MEMORY] " \
+ "which contains information relevant to your conversation with the user. "

message = [
    SystemMessage(content=system_prompt ),
    SystemMessage(content="[MEMORY]\n" + json.dumps(agent_memory)),
    HumanMessage(content="My name is Bob.")
]


llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke(message)

# %%
print(response)
additional_kwargs =  response.additional_kwargs
# ad_kwarg_dict = json.loads(additional_kwargs)

function_call = additional_kwargs.get("function_call", {})

arguments = function_call.get("arguments", {})
print("Function Call Arguments:", arguments)
# print(additional_kwargs.function_call.arguments) Giving error ?
# `dict` like {'a':'b'} is a class where a is not an attribute of the class but `keys()`` is a method of the class. to access a particular key use square brackett notations like `dict['a']` or `dict.get('a')` to get the value of key 'a'.

# You are able to do `response.additional_kwargs` because `additional_kwargs` is a attribute of the response object's class. so dor notion is valid.


# %%
print(agent_memory)
update_core_agent_memory(**json.loads(arguments))
agent_memory

# %%
response =  llm_with_tools.invoke([
    SystemMessage(content=system_prompt ),
    SystemMessage(content="[MEMORY]\n" + json.dumps(agent_memory)),
    HumanMessage(content="What is my name?")
])

response = llm_with_tools.invoke(message)
print(response)


# %%
additional_kwargs =  response.additional_kwargs
# ad_kwarg_dict = json.loads(additional_kwargs)

function_call = additional_kwargs.get("function_call", {})

arguments = function_call.get("arguments", {})
print("Function Call Arguments:", arguments)
update_core_agent_memory(**json.loads(arguments))
agent_memory

# %%
response =  llm_with_tools.invoke([
    SystemMessage(content=system_prompt ),
    SystemMessage(content="[MEMORY]\n" + json.dumps(agent_memory)),
    HumanMessage(content="What is Javascript?"),
    HumanMessage(content="What is Javascript?")
])

response = llm_with_tools.invoke(message)
print(response)

# %%
update_core_agent_memory_properties = \
{
    "section":{
        "type": "string",
        "enum": ["human", "interaction_context_till_now", "agent"],
        "description": "The section of memory to update. Must be either  'human'(to save information about human), 'interaction_context_till_now'(to save the main context of all the previous talks held till now(having higher proportions of recent talks) in most summarized phrase form which is easy to understand or recall and get stored in minimal space, "
        " ), or 'agent'(to store information about yourself)."
    },

    "updated_memory": {
        "type": "string",
        "description": "The new memory content to set for the specified section. It should be a concise and relevant update."
    }
}


update_core_agent_memory_description = "Update the important information about you(the agent), or the whatever interaction context you have with the user or about the human you are interacting with. Here for the interaction context, you can save the main context of all the previous talks held till now(having higher proportions of recent talks) in most summarized phrase form which is easy to understand or recall and get stored in minimal space, so that you can use it in the future to recall the context of the conversation without having to go through all the previous messages."

update_core_agent_memory_metadata = \
{
    "type": "function",
    "function": {
        "name": "update_core_agent_memory",
        "description": update_core_agent_memory_description,
        "parameters": {
            "type": "object",
            "properties": update_core_agent_memory_properties,
            "required": ["section", "updated_memory"]
        }
    }

}


