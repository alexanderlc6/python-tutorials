from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
import os

def get_weather(city:str) -> str:
    return f"It's sunny in {city}"

model = ChatOpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model='qwen-max',
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

agent = create_agent(
    model = model,
    tools=[get_weather],
    system_prompt='You are a helpful assistant'
)

# Run the agent
res = agent.invoke(SystemMessage(content="what is the weather in sf"))
# res = agent.invoke({'message': [{'role':'user', 'content': 'what is the weather in sf'}]})
print(res)