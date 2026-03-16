from typing import Any, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.func import entrypoint, task
from langgraph.graph import StateGraph, MessagesState
from sqlalchemy.sql.annotation import Annotated
from operator import add

checkpointer = InMemorySaver()

@entrypoint(checkpointer=checkpointer)
def my_workflow(number: int, *, previous: Any = None) -> int:
    previous = previous or 0
    return number + previous

config = {
    'configurable': {
        'thread_id': 'some_thread_id'
    }
}

# Output: 1 and 3
print(my_workflow.invoke(1, config))
print(my_workflow.invoke(2, config))

# Using entrypoint.final demo
@entrypoint(checkpointer=checkpointer)
def my_workflow(number: int, *, previous: Any = None) -> entrypoint.final[int, int]:
    previous = previous or 0
    return entrypoint.final(value=previous, save=2*number)

@task()
def slow_computation(input_value):
    # Simulate a long-running operation
    pass

config = {
    'configurable': {
        'thread_id': '1'
    }
}

# Output: 0 and 6
print(my_workflow.invoke(3, config))
print(my_workflow.invoke(1, config))

class StateObj(TypedDict):
    foo: int
    messages: Annotated[list[str], add]
def plain_node1(state: StateObj):
    return state

graph = StateGraph(MessagesState)
graph.add_node(plain_node1)
graph.add_edge(START, 'plain_node1')
graph.add_edge('plain_node1', END)
graph = graph.compile(checkpointer=checkpointer)
# {'messages': [HumanMessage(content='hi! i am Bob', additional_kwargs={}, response_metadata={}, id='531167bf-e5ef-46ca-9af9-ee752d6f1abf')]}
print(graph.invoke(
    {"messages": [{"role": "user", "content": "hi! i am Bob"}]},
    config
))


