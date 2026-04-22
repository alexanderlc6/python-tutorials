from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model='gpt-4-turbo-preview', temperature=0.5)

# Config tools
from langchain_community.agent_toolkits.load_tools import load_tools
tools = load_tools(['serpapi', 'llm-math'], llm=llm)

# Config prompt template
from langchain_core.prompts import PromptTemplate
template = (
    '''
    '尽量用中文回答如下问题，如果能力不够可以使用如下工具:\n\n'
    '{tools}\n\n
    Use the following format:\n\n'
    'Question: the input question you must answer\n'
    'Thought: you should think about what to do\n'
    'Action: the action to take, should be one of [{tool_names}]\n'
    'Action Input: the input to the action\n'
    'Observation: the result of the action\n'
    '...(This Thought/Action/Action Input/Observation can repeat n times.)\n'
    'Thought: I now know the final answer\n'
    'Final answer: the final answer to the original input question\n\n'
    'Begin!\n\n'
    'Question: {input}\n'
    'Thought:{agent_scratchpad}'
    '''
)
prompt = PromptTemplate.from_template(template)

# Init agent
from langchain.agents import create_react_agent
agent = create_react_agent(llm, tools, prompt)

# Build AgentExecutor
from langchain.agents import AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)