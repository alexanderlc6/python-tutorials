from accelerate.commands.config.update import description
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
from langchain_experimental.autonomous_agents import AutoGPT
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
import os

from langchain_core.vectorstores import InMemoryVectorStore
embeddings = DashScopeEmbeddings(model='text-embedding-v3',
                             dashscope_api_key=os.getenv('DASHSCOPE_API_KEY'))
vector_store = InMemoryVectorStore(embeddings)

tools = []
search = SerpAPIWrapper()
tools.append(Tool(
    name='search',
    function=search.run,
    description='search online'
))

agent = AutoGPT.from_llm_and_tools(
    ai_name='AlexAgent',
    ai_role='Assistant',
    tools=tools,
    llm=ChatOpenAI(model='gpt-4', temperature=0, verbose=True),
    memory=vector_store.as_retriever(
        search_type='similarity_score_threshold',
        search_kwargs={'score_threshold': 0.8}
    ),
)

agent.chain.verbose=True
agent.run(['What the goal number of Chinese team Olympic Games in recent years?'])