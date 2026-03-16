from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from typing import TypedDict
from langgraph.types import Send
import operator
from typing import Annotated, TypedDict
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: int
    # State would then be {"foo": 2, "bar": ["hi", "bye"]}
    bar: Annotated[list[str], add]

def plain_node1(state: State):
    return state

# Define shared structure all over nodes in the graph
class OverallState(TypedDict):
    subjects: list[str]
    jokes: Annotated[list[str], operator.add]

def continue_to_jokes(state: OverallState):
    # Dynamically generate Send objects and fan out parallelly
    # (Map-Reduce design pattern: send and aggregate sub-tasks results to a list)
    return [Send('generate_joke', {'subject': s}) for s in state['subjects']]

builder = StateGraph(OverallState)
# builder.add_node(plain_node1)
# builder.add_conditional_edges('plain_node1', continue_to_jokes)
builder.add_node('generate_joke', lambda state: {'jokes': [f'About {state['subject']} joke']})
builder.add_conditional_edges(START, continue_to_jokes)
builder.add_edge('generate_joke', END)

graph = builder.compile()
result = graph.invoke({'subjects':['Cat','Dog']})

# {'subjects': ['Cat', 'Dog'], 'jokes': ['About Cat joke', 'About Dog joke']}
print(result)