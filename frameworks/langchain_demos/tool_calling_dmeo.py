from langchain.tools import tool
import os
from langchain_openai import ChatOpenAI
# Or use lib: from langchain_community.chat_models import ChatTongyi
# Do not support: from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_core.callbacks import UsageMetadataCallbackHandler

@tool(description='Get the weather')
def get_weather(location:str) -> str:
    return f"It's sunny in {location}"

# Define server-side tool
web_search_tool = {'type': 'web_search'}

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  # <-- Can only make a request once every 10 seconds!!
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10  # Controls the maximum burst size.
)
model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                   rate_limiter=rate_limiter,
                   temperature=0
                   ).bind(logprobs=True)
# Or use below method
# model = ChatTongyi(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
#                    rate_limiter=rate_limiter).bind(logprobs=True)
# Do not support model provider [tongyi] currently
# model = init_chat_model('qwen-max', model_provider='tongyi',api_key=os.getenv('DASHSCOPE_API_KEY'))

# Step 1: Model generates tool calls
model_with_tools = model.bind_tools([get_weather, web_search_tool])

callback = UsageMetadataCallbackHandler()

# Step 2: Single calling
response = model_with_tools.invoke("What's the weather like in Shanghai?", config={ 'configurable': {'model': 'qwen-max'}})
for tool_call in response.tool_calls:
    print(f'Tool: {tool_call['name']}')
    print(f'Args: {tool_call['args']}')
print(response.content_blocks)
# print(response.tool_calls)

response = model.invoke("Why do parrots talk?",
                        config={
                                 'run_name': 'test_tool_call',
                                 'tags': ['human', 'query'],
                                 'metadata': { "user_id": "101"},
                                 'callbacks': [callback],
                                'configurable': {'model': 'qwen-max'}
                                }
                        )
print(response.response_metadata['logprobs'])
print(callback.usage_metadata)

# Step 2: Tool execution loop
# messages = [{'role':'user', 'content':'What is the weather like in Shanghai?'}]
# ai_msg = model_with_tools.invoke(messages)
# messages.append(ai_msg)
# print(messages)
#
# for tool_call in ai_msg.tool_calls:
#     tool_result = get_weather.invoke(tool_call)
#     # content="It's sunny in Shanghai" name='get_weather' tool_call_id='call_e19b00dc9e3f414fa3433e'
#     print(tool_result)
#     messages.append(tool_result)
#
# # Step 3: Pass results back to model for final response
# final_response = model_with_tools.invoke(messages)
# print(final_response.text)