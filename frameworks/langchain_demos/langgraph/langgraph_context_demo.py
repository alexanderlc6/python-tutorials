from dataclasses import dataclass
from typing import TypedDict, Annotated
import operator
from langchain_core.runnables import RunnableConfig
import os

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.runtime import Runtime

# Define Graph state structure
class State(TypedDict):
    messages: Annotated[list, operator.add]
    counter: int
    input: str
    result: str

# Define Context Schema
@dataclass
class ContextSchema:
    llm_provider: str = 'openai'
    api_key: str = None

def get_llm(provider:str):
    if provider == 'openai':
        from langchain_openai import ChatOpenAI
        return ChatOpenAI()
    elif provider == 'anthropic':
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic()
    else:
        raise ValueError(f'Invalid LLM provider:{provider}')

def node_a(state: State, runtime: Runtime[ContextSchema], config: RunnableConfig[ContextSchema]) -> State:
    context: ContextSchema = config['configurable']
    llm = get_llm(runtime.context.llm_provider)

    result = llm.invoke('Hello')
    return {'messages': [result.content], 'counter': state['counter'] + 1}

def node_b(state: State, config: RunnableConfig[ContextSchema]) -> State:
    return {
        'messages': ['Processed by node_b'], 'counter': state['counter'] + 1
    }

def build_graph():
    graph = StateGraph(State, context_schema=ContextSchema)
    graph.add_node('node_a', node_a)
    graph.add_node('node_b', node_b)
    graph.set_entry_point('node_a')
    graph.add_edge('node_a', 'node_b')
    graph.add_edge('node_b', END)
    return graph.compile()

if __name__ == '__main__':
    graph = build_graph()
    init_state = {'messages': [], 'counter': 0}
    config = {'configurable': ContextSchema(llm_provider='anthropic', api_key=os.getenv('ANTHROPIC_API_KEY'))}
    # result = graph.invoke(inputs, context = {'llm_provider':'anthropic'})
    result = graph.invoke(init_state, config)
    print(result)