import dataclasses
import uuid
from typing import Any, TypedDict

from langchain_core.stores import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.func import entrypoint, task
from langgraph.graph import StateGraph, MessagesState
from langgraph.runtime import Runtime
from sqlalchemy.sql.annotation import Annotated
from operator import add
from dataclasses import dataclass

# Add short-term memory
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

# Add long-term memory
store = InMemoryStore()

@dataclass
class Context:
    user_id: str

async def call_model(state: MessagesState, runtime: Runtime[Context]):
    user_id = runtime.context.user_id
    namespace = (user_id, 'memories')

    # Search for relevant memories
    memories = await runtime.store.asearch(namespace, query=store['messages'][-1].content, limit=3)
    info = '\n'.join([d.value['data'] for d in memories])

    # ... Use memories in model call
    # Store a new memory
    await runtime.store.aput(
        namespace, str(uuid.uuid4()), {'data': 'User prefers dark mode'}
    )

builder = StateGraph(MessagesState, context_schema=Context)
builder.add_node(call_model)
builder.add_edge(START, 'call_model')
# builder.add_edge('call_model', END)
graph = builder.compile(checkpointer=checkpointer, store=store)
# {'messages': [HumanMessage(content='hi! i am Bob', additional_kwargs={}, response_metadata={}, id='531167bf-e5ef-46ca-9af9-ee752d6f1abf')]}

# Pass context at invocation time
print(graph.invoke(
    {"messages": [{"role": "user", "content": "Hi! I am Bob"}]},
    config,
    context = Context(user_id='123')
))



