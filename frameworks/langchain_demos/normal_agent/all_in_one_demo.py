from dataclasses import dataclass
from typing import Any

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model, after_model, SummarizationMiddleware
from langchain.tools import tool
from langchain_core.messages import RemoveMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.tools import ToolRuntime
import os

from langgraph.runtime import Runtime


@tool
def get_weather_for_location(city:str) -> str:
    """Get weather for a given city."""
    return f"It's sunny in {city}"

@dataclass
class CustomContext():
    user_id: str

@tool
def get_user_location(runtime: ToolRuntime[CustomContext]) -> str:
    """Retrieve user information based on user ID."""
    user_id = runtime.context.user_id
    return 'Florida' if user_id == '123' else 'New York'

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# Get runtime info inside tool
@tool
def fetch_user_email_preferences(runtime: ToolRuntime(CustomContext)) -> str:
    """Fetch the user's email preferences from the store."""
    user_id = runtime.context.user_id

    preference: str = 'The user prefers you to write a brief and polite email.'
    if runtime.store:
        if memory := runtime.store.get(('users',), user_id):
            preference = memory.value['preference']

    return preference

@dataclass
class ResponseFormat:
    """Response schema for the agent."""
    punny_response: str
    weather_condition: str | None = None

class CustomerAgentState(AgentState):
    user_id: str
    preferences: dict

@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Keep only the last few messages to fit context window."""
    messages = state['messages']

    if len(messages) <= 3:
        return None

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    # State updates to merge into the agent state
    return {
        'messages':[
            RemoveMessage(id = REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }

@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove old messages to keep conversation manageable."""
    messages = state['messages']
    if len(messages) > 2:
        # remove the earliest two messages
        return {
            'messages': [
                RemoveMessage(id=m.id) for m in messages[:2]
                # To remove all messages
                # RemoveMessage(id=REMOVE_ALL_MESSAGES)
            ]
        }

    return None

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """Remove messages containing sensitive words."""
    STOP_WORDS = ['password','secret']
    last_msg = state['messages'][-1]
    if any(word in last_msg.content for word in STOP_WORDS):
        return {'messages': RemoveMessage(id=last_msg.id)}
    return None

# Read short-term memory in a tool
@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """Look up user info."""
    user_id = runtime.state['user_id']
    return 'User is Sally' if user_id == 'user123' else 'User is not found'

agent = create_agent(
    model=model,
    tools= [
            get_weather_for_location, get_user_location, get_user_info,
            ],
    system_prompt='Please be concise and to the point.',
    checkpointer = InMemorySaver(),
    state_schema= CustomerAgentState,
    middleware=[
        trim_messages,
        delete_old_messages,
        validate_response,
        SummarizationMiddleware(
            model=model,
            trigger=('tokens', 4000),
            keep=('messages', 20)
        )
    ]
)

config: RunnableConfig = {'configurable': {'thread_id': 1}}
result = agent.invoke(
    {
        # 'messages': [{'role': 'user', 'content': 'Hello, my name is Alex.'}],
        # Request to look up user info
        'messages': 'look up user information',
        # Custom state can be passed in invoke
        'user_id': 'user123',
        'preference': {'theme': 'dark'}
    },
    config
)
# agent.invoke({"messages": "write a short poem about cats"}, config)
# agent.invoke({"messages": "now do the same but for dogs"}, config)
# final_response = agent.invoke({"messages": "what's my name?"}, config)

# final_response['messages'][-1].pretty_print()
    # Direct Output:
    # ================================== Ai Message ==================================
    #
    # Your name is Alex. You mentioned it at the beginning of our conversation.

# Output with stream of synchronous mode
# for event in agent.stream(
#         {'messages': [{'role': 'user', 'content': 'Hello, I am Alex'}]},
#         config,
#         stream_mode='values'
# ):
#     print([(message.type, message.content) for message in event['messages']])
#
# for event in agent.stream(
#         {'messages': [{'role': 'user', 'content': "What's my name?"}]},
#         config,
#         stream_mode='values'
# ):
#     print([(message.type, message.content) for message in event['messages']])

# Output with stream of asynchronous mode
# async def main():
#     async for event in agent.astream(
#             {'messages': [{'role': 'user', 'content': 'Hello, I am Alex'}]},
#             config,
#             stream_mode='values'
#     ):
#         print([(message.type, message.content) for message in event['messages']])
#
#     async for event in agent.astream(
#             {'messages': [{'role': 'user', 'content': "What's my name?"}]},
#             config,
#             stream_mode='values'
#     ):
#         print([(message.type, message.content) for message in event])
# Output:
# [('human', 'Hello, my name is Alex.'), ('ai', 'Hello Alex! How can I assist you today?'), ('human', 'Hello, I am Alex')]
# [('human', 'Hello, my name is Alex.'), ('ai', 'Hello Alex! How can I assist you today?'), ('human', 'Hello, I am Alex'), ('ai', 'Hello Alex! How may I assist you today?')]
# [('human', 'Hello, my name is Alex.'), ('ai', 'Hello Alex! How can I assist you today?'), ('human', 'Hello, I am Alex'), ('ai', 'Hello Alex! How may I assist you today?'), ('human', "What's my name?")]
# [('human', 'Hello, my name is Alex.'), ('ai', 'Hello Alex! How can I assist you today?'), ('human', 'Hello, I am Alex'), ('ai', 'Hello Alex! How may I assist you today?'), ('human', "What's my name?"), ('ai', 'Your name is Alex. How can I assist you further?')]

# if __name__ == '__main__':
#     asyncio.run(main())

# Look up result
print(result['messages'][-1].content)
# The user's information has been looked up. The user is Sally.