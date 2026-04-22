from typing import Literal

from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import os

from tavily import TavilyClient

model = ChatOpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model='qwen-max'
)

@tool
def get_weather(city:str) -> str:
    """Get the current weather for a given city."""
    return f"It's sunny in {city}"

agent = create_deep_agent(
    model=model,
    tools=[get_weather],
    system_prompt='You are a helpful assistant'
)

# Run the agent
res = agent.invoke(
    {'message': [{'role':'user', 'content': 'what is the weather in sf'}]}
)
print(res)
#Output:
# {'messages': [AIMessage(content='您好！请问有什么我可以帮您的？如果您有具体的任务或问题，请告诉我详细信息，我将立即着手处理。', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 25, 'prompt_tokens': 5699, 'total_tokens': 5724, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-max', 'system_fingerprint': None, 'id': 'chatcmpl-78bd9b47-1a4f-9aa3-a752-6a56cce43bdb', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019cfb8d-29a7-75a3-9c77-ffbc051a9f72-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 5699, 'output_tokens': 25, 'total_tokens': 5724, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}})]}

tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

@tool(description='internet_search function')
def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal['general', 'news', 'finance'] = 'general',
        include_raw_content: bool = False
):
    # Run web search
    results = tavily_client.search(query, max_results=max_results, include_raw_content=include_raw_content, topic=topic)
    print([result.to_dict() for result in results])
    return results

# research_instructions='''
# You are a helpful assistant.
# You are given a query and a set of search results.
# Your task is to answer the query based on the search results.
# If the query is not clear, you should ask for more information.
# If the query is not relevant to the search results, you should say so.
# If the query is relevant to the search results, you should answer the query based on the search results.
# If the query is not relevant to the search results, you should say so.
# If the query is not clear, you should ask for more information.
# If the query is not relevant to the search results, you should say so.
# '''
research_instructions = '''You are an expert researcher. Your job is to conduct thorough research and then write a polished report.
You have access to an internet search tool as your primary means of gathering information.
## `internet_search`
Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
'''

agent = create_deep_agent(
    model=model,
    tools=[internet_search],
    system_prompt=research_instructions
)
result = agent.invoke({'messages': [{'role': 'user', 'content': 'What is AI agent?'}]})
print(result['messages'][-1].content)
