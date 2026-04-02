from langchain_classic.chains.llm_math.base import LLMMathChain
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI()

# Create tool
search = SerpAPIWrapper()
llm_math_chain = LLMMathChain(llm=llm, verbose=True)

# Define tools list
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    )
]