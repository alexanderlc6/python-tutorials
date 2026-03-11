import os
from langchain import hub
from langchain.agents import AgentExecutor, create_self_ask_with_search
from langchain_community.tools.tavily_search import TavilyAnswer
from dotenv import load_dotenv

load_dotenv()

# Config model
from langchain_fireworks import Fireworks

llm = Fireworks(
    api_key = os.getenv('FIREWORKS_API_KEY'),
    model="accounts/fireworks/models/llama-v3p1-405b-instruct", max_tokens = 256)
tools = [TavilyAnswer(max_results=1, name='Mid answer')]

# Get prompt
prompt = hub.pull("hwchase17/self_ask_with_search")
print(prompt)

agent = create_self_ask_with_search(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
print(agent_executor.invoke({'input':'Who is Mao Zedong?'}))