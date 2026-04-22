import asyncio
import re
import uuid
from typing import Any, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.func import entrypoint, task
from langgraph.graph import StateGraph, MessagesState
from langgraph.runtime import Runtime
from langgraph.store.postgres import AsyncPostgresStore
from sqlalchemy.sql.annotation import Annotated
from operator import add
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
import os

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0)
# model = init_chat_model(model='gpt-5.1', api_key=os.getenv('OPENAI_API_KEY'),
#                         base_url='https://api.chatanywhere.tech')

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

# Sync call mode
# def call_model(state: MessagesState, runtime: Runtime[Context]):
#     user_id = runtime.context.user_id
#     namespace = (user_id, 'memories')
#
#     # Search for relevant memories
#     memories = store.search(namespace, query=state['messages'][-1].content, limit=3)
#     info = '\n'.join([d.value['data'] for d in memories]) if memories else ''
#     print(f'Found memories: {info}')
#
#     # ... Use memories in model call
#     # Store a new memory
#     store.put(namespace, str(uuid.uuid4()), {'data': 'User prefers dark mode'})
#     return {'messages': state['messages']}
#
# builder = StateGraph(MessagesState, context_schema=Context)
# builder.add_node(call_model)
# builder.add_edge(START, 'call_model')
# # builder.add_edge('call_model', END)
# graph = builder.compile(checkpointer=checkpointer, store=store)
# # {'messages': [HumanMessage(content='hi! i am Bob', additional_kwargs={}, response_metadata={}, id='531167bf-e5ef-46ca-9af9-ee752d6f1abf')]}
#
# # Pass context at invocation time
# result = graph.invoke(
#     {"messages": [{"role": "user", "content": "Hi! I am Bob"}]},
#     config,
#     context = Context(user_id='123')
# )
# print('Result:', result)

# ------------------------------------------------------------------------------------
# In production, using DB storage instead
# Use Postgresql
from langgraph.checkpoint.postgres import PostgresSaver
DB_URI = 'postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable'

# Async call mode
async def call_model(
    state: MessagesState,
    runtime: Runtime[Context]
):
    user_id = runtime.context.user_id
    # Create namespace to isolate user data
    namespace = ('memories', user_id)
    # Search for relevant memories(not explicitly match) by current user's question
    memories = await runtime.store.asearch(namespace, query=state['messages'][-1].content)
    # Join memory result to system message and send to LLM again
    info = '\n'.join([d.value['data'] for d in memories])
    system_msg = SystemMessage(content=f'You are a helpful assistant talking to the user. User info: {info}')

    # Store new memories if the user asks the model to remember
    last_message = state['messages'][-1]

    content = last_message.content
    if 'remember' in content.lower():
        # Memory text Resolve Method1: Dynamic resolve user's memory request text manually with regex
        # Fixed memory = 'User name is David'
        memories_to_store = []
        # Get name info
        name_match = re.search(r'my name is (\w+)', content, re.IGNORECASE)
        if name_match:
            name = name_match.group(1)
            memories_to_store.append(f'User name is {name}')

        # Get hometown info
        hometown_match = re.search(r'my hometown is (?:in\s+)?([^,.]+)', content, re.IGNORECASE)
        if hometown_match:
            hometown = hometown_match.group(1)
            memories_to_store.append(f'User hometown is {hometown}')

        # Store all user's memories
        for memory in memories_to_store:
            await runtime.store.aput(namespace, str(uuid.uuid4()), {'data': memory})
            print(f'Stored memory: {memory}')

        # Memory text Resolve Method2: Dynamic resolve with LLM
        # extraction_prompt = f'''Extract personal information from this message as a list of facts.
        # Message: {content}
        # Format each fact as a sample sentence like 'User [attribute] is [value].'
        # Only include factual information the user wants to remember.
        # Facts: '''
        # extraction_response = await model.ainvoke(
        #     {'role': 'user', 'content': extraction_prompt}
        # )
        # facts = extraction_response.content.strip().strip('\n')
        #
        # for fact in facts:
        #     fact = fact.strip()
        #     if fact and fact.lower().startswith('user'):
        #         await runtime.store.aput(namespace, str(uuid.uuid4()), {'data': fact})
        #         print(f'Stored fact: {fact}')

    # print(f"Messages type: {type(state['messages'])}")
    # print(f"First message type: {type(state['messages'][0])}")    # HumanMessage type
    # print(f"First message: {state['messages'][0]}")

    response = await model.ainvoke(
        # [{'role': 'system', 'content': system_msg}] + state['messages']
        [system_msg] + state['messages']
    )

    return {'messages': response}

async def main():
    async with (
        AsyncPostgresStore.from_conn_string(DB_URI) as store,
        AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer

        # Use Redis as storage
        # AsyncRedisStore.from_conn_string(REDIS_URI) as store,
        # AsyncRedisSaver.from_conn_string(REDIS_URI) as checkpointer
    ):
        await store.setup()
        await checkpointer.setup()
        builder = StateGraph(MessagesState, context_schema=Context)
        builder.add_node(call_model)
        builder.add_edge(START, 'call_model')
        graph = builder.compile(checkpointer=checkpointer, store=store)

        config = {
            'configurable': {
                'thread_id': '1'
            }
        }

        async for chunk in graph.astream(
                {'messages': [{'role': 'user', 'content': 'Hello!Remember: My name is David, my hometown is in Shanghai,China.'}]},
                config,
                stream_mode='values',
                context = Context(user_id='123')
        ):
            chunk['messages'][-1].pretty_print()

        config = {
            'configurable': {
                'thread_id': '2'
            }
        }

        async for chunk in graph.astream(
        {'messages': [
                    {'role': 'user', 'content': 'What is my name?'},
                    {'role': 'user', 'content': 'Where is my hometown?'}
             ]},
            config,
            stream_mode='values',
            context = Context(user_id='123')
        ):
            chunk['messages'][-1].pretty_print()
        # print('Graph state:', graph.get_state(config))

if __name__ == '__main__':
    asyncio.run(main())

# Output:
# ================================ Human Message =================================
#
# Hello!Remember: My name is David, my hometown is in Shanghai,China.
# Stored memory: User name is David
# Stored memory: User hometown is Shanghai
# ================================== Ai Message ==================================
#
# Hello David! I remember that your name is David and your hometown is in Shanghai, China.
#
# How can I assist you today? Is there anything specific you'd like to discuss or any questions you have?
# ================================ Human Message =================================
#
# Where is my hometown?
# ================================== Ai Message ==================================
#
# Your name is David.
#
# Your hometown is Shanghai.