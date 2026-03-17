"""Research Agent Demo- Standalone script for LangGraph deployment.

This module creates a deep research agent with custom tools and prompts
for conducting web research with strategic thinking and context management.
"""
from datetime import datetime
import os
from deepagents import create_deep_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from research_agent.prompts import (
    RESEARCHER_INSTRUCTIONS,
    RESEARCH_WORKFLOW_INSTRUCTIONS,
    SUBAGENT_DELEGATION_INSTRUCTIONS
)

from research_agent.call_tools import tavily_search, think_tool

# Limits
max_concurrent_research_units = 3
max_researcher_iterations = 3

# Get current data
current_date = datetime.now().strftime('%Y-%m-%d')

# Combine orchestrator instructions
INSTRUCTIONS = (
    RESEARCH_WORKFLOW_INSTRUCTIONS
    + '\n\n'
    + '=' * 80
    + '\n\n'
    + SUBAGENT_DELEGATION_INSTRUCTIONS.format(
        max_concurrent_research_units=max_concurrent_research_units,
        max_researcher_iterations=max_researcher_iterations
    )
)

# Create research sub-agent
research_sub_agent = {
    'name': 'Research Agent',
    'description': 'Delegate research to the sub-agent researcher. Only give this researcher one topic at a time.',
    'system_prompt': RESEARCHER_INSTRUCTIONS.format(date=current_date),
    'tools': [tavily_search, think_tool]
}

# Model qwen-max
model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
agent = create_deep_agent(
    model=model,
    tools=[tavily_search, think_tool],
    system_prompt=INSTRUCTIONS,
    subagents=[research_sub_agent]
)
print(agent.invoke(SystemMessage(content = 'What is quantum computing?')))
