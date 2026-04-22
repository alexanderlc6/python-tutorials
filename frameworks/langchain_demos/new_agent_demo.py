from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, dynamic_prompt
from langchain.tools import tool
import os
from typing import Callable
from langchain.messages import ToolMessage, SystemMessage, HumanMessage

# Force to use Pydantic V2 mode
os.environ["LANGCHAIN_PYDANTIC_V2"] = "1"

model = ChatOpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model='qwen-max',
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

# base_model = ChatOpenAI(model='gpt-4.1-mini')
# advanced_model = ChatOpenAI(model='gpt-4.1')
base_model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
advanced_model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-plus',base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    # Choose model based on context complexity
    msg_count = len(request.state['messages'])

    # if msg_count > 10:
    #     model = advanced_model
    # else:
    #     model = base_model

    return handler(request.override(model=model))

@tool(description='Useful for when you need to add numbers')
def calculator(a, b):
    return a + b

@tool(description='Useful for when you need to find information')
def search(query:str) -> str:
    return f'Result for {query}'

@tool(description='Useful for when you need to know the weather')
def get_weather(city:str) -> str:
    return f"It's sunny in {city}"

'''
Best use below method when:
1) All possible tools are known at compile/startup time
2) You want to filter based on permissions, feature flags, or conversation state
3) Tools are static but their availability is dynamic
'''
@wrap_model_call()
def state_based_tools(request: ModelRequest,
                      handle: Callable[[ModelRequest], ModelResponse]) -> ModelResponse:
    # Filter tools based on conversation State
    # Read from State: check if user has authenticated
    state = request.state
    is_authenticated = state.get('authenticated', False)
    msg_count = len(state['messages'])

    # Only enable sensitive tools after authentication
    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith('public_')]
        request = request.override(tools = tools)
    elif msg_count < 5:
        # Limit tools early in conversation
        tools = [t for t in request.tools if t.name != 'advanced_search']
        request = request.override(tools = tools)

    return handle(request)

# Handle errors or exceptions
@wrap_model_call
def handle_tool_errors(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(tool_call_id=request.tool_call_id,
                           name='error',
                           content=f'Tool Error: Please check your input and try again.({str(e)}',
                           finish_reason='tool_error')

agent = create_agent(
    model=model, tools=[search, calculator, get_weather], middleware=[dynamic_model_selection, handle_tool_errors],
    system_prompt='You are a helpful assistant. Be concise and accurate.'
)
# agent = create_agent(model=model, tools=[public_search,private_search,advanced_search],
#                      middleware=state_based_tools, handle_tool_errors)
literary_agent = create_agent(model=model,
                              system_prompt=SystemMessage(
                                  content=[
                                    {
                                        "type": "text",
                                        "text": "You are an AI assistant tasked with analyzing literary works.",
                                    },
                                    {
                                        "type": "text",
                                        "text": "<the entire contents of 'Pride and Prejudice'>",
                                        "cache_control": {"type": "ephemeral"}
                                    }
                                  ]
                              ))
result = literary_agent.invoke({'messages': [HumanMessage("Analyze the major themes in 'Pride and Prejudice'.")]}
                               )