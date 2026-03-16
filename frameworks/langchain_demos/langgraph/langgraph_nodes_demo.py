from codeop import CommandCompiler
from dataclasses import dataclass
from typing_extensions import TypedDict, Literal

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
import time
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy, Command, Interrupt, interrupt


class State(TypedDict):
    input: str
    results: str

    # Test memory cache function
    x: int
    result: int

@dataclass
class Context:
    user_id: str

builder = StateGraph(State)

def plain_node(state: State):
    return state

def node_with_runtime(state: State, runtime: Runtime[Context]):
    print('In node:', runtime.context.user_id)
    return {'results': f'Hello {state['input']}!'}

def node_with_config(state: State, config: RunnableConfig):
    print('In node with thread:', config['configurable']['thread_id'])
    return {'results': f'Hello {state['input']}!'}

# Define Commands for a node route to a different node
def my_node(state: State) -> Command[Literal['plain_node']]:
    # if(state['x'] == 45):
    #     return Command(update={'x': 45}, goto='plain_node')
    return Command(
        # State update
        update={'x': 45},
        # Control flow
        goto='plain_node',
        # Route to node in parent graph
        # graph=Command.PARENT
    )

def human_review(state: State):
    # Pauses the graph and waits for a value
    answer = interrupt('Do not approve?')
    return {'messages': [{'role': 'user', 'content': answer}]}

builder.add_node('plain_node', plain_node)
builder.add_node('node_with_runtime', node_with_runtime)
builder.add_node('node_with_config', node_with_config)

def expensive_node(state: State) -> dict[str, int]:
    time.sleep(2)
    return {'result': state['x'] * 2}
builder.add_node('expensive_node', expensive_node, cache_policy=CachePolicy(ttl=3))
builder.set_entry_point('expensive_node')
builder.set_finish_point('expensive_node')

graph = builder.compile(cache=InMemoryCache())

# [{'expensive_node': {'result': 10}}]
print(graph.invoke({'x': 5}, stream_mode = 'updates'))
# [{'expensive_node': {'result': 10}, '__metadata__': {'cached': True}}]
print(graph.invoke({'x': 5}, stream_mode = 'updates'))

# First invocation - hits the interrupt and pauses
result = graph.invoke({'messages': [...]}, config)
# Resume with a value - the interrupt() call returns "yes"
result = graph.invoke(Command(resume='yes'), config)