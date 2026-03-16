from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.types import StreamWriter

in_memory_checkpointer = InMemorySaver()
in_memory_store = InMemoryStore()

@entrypoint(checkpointer=in_memory_checkpointer, store=in_memory_store)

def my_workflow(some_input: dict, *,
                previous: Any = None, # For short-term memory
                store: BaseStore, # For long-term memory
                writer: StreamWriter, # For streaming custom data
                config: RunnableConfig # For accessing the configuration passed to the entrypoint
                ) -> ...:
    pass