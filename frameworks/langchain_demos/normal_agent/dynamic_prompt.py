import dataclasses
from typing import TypedDict

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import dynamic_prompt, ModelRequest, before_model, after_model
from langchain_openai import ChatOpenAI
import os
from dataclasses import dataclass

from langgraph.runtime import Runtime

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

# class CustomerContext(TypedDict):
@dataclass
class CustomerContext:
    user_name: str

def get_weather(city: str) -> str:
    """Get the weather in a city."""
    return f"It's sunny in {city}"

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context.user_name
    system_prompt = f'You are a helpful assistant. Address the user as {user_name}."'
    return system_prompt

@before_model
def log_before_model(state: AgentState, runtime: Runtime[CustomerContext]) -> dict | None:
    print(f"Processing request for user: {runtime.context.user_name}")
    return None

@after_model
def log_after_model(state: AgentState, runtime: Runtime[CustomerContext]) -> dict | None:
    print(f"Completed request for user: {runtime.context.user_name}")
    return None

agent = create_agent(
    model=model,
    tools=[get_weather],
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=CustomerContext
)

result = agent.invoke(
    # {'messages': [{'role': 'user', 'content': 'What is the weather in New York?'}]},
{'messages': [{'role': 'user', 'content': 'What is my name?'}]},
    context=CustomerContext(user_name='Joe')
)

for msg in result['messages']:
    msg.pretty_print()

# Output:
# ================================ Human Message =================================
#
# What is the weather in New York?
# ================================== Ai Message ==================================
# Tool Calls:
#   get_weather (call_f6f758a241634be1b4d315)
#  Call ID: call_f6f758a241634be1b4d315
#   Args:
#     city: New York
# ================================= Tool Message =================================
# Name: get_weather
#
# It's sunny in New York
# ================================== Ai Message ==================================
#
# It's sunny in New York, Joe.

# Test executing before and after model
# Processing request for user: Joe
# Completed request for user: Joe
# ================================ Human Message =================================
#
# What is my name?
# ================================== Ai Message ==================================
#
# Your name is Joe.