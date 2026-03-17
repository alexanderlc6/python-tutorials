import asyncio

from langchain.embeddings import init_embeddings
from langgraph.constants import START
from langgraph.graph import MessagesState, StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI
import os

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0)

embeddings = init_embeddings('text-embedding-v3',
                             api_key=os.getenv('DASHSCOPE_API_KEY'),
                             base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
store =InMemoryStore(
    index={
        'embed': embeddings,
        'dims': 1536
    }
)
store.put(('user_1', 'memories'), '1', {'text': 'I like cat'})
store.put(('user_1', 'memories'), '2', {'text': 'I am a scientist'})

async def chat(state: MessagesState, runtime: Runtime):
    # Search based on user's last message
    items = await runtime.store.asearch(
        ('user_1', 'memories'), query=state['messages'][-1].content, limit=2
    )
    memories = '\n'.join(item.value['text'] for item in items)
    memories = f'##Memories of user\n{memories}' if memories else ''
    response = await model.ainvoke(
        {'role':'system',
         'content': f'You are a helpful assistant.\n{memories}'},
        *state['messages']
    )
    return {'messages': [response]}

builder = StateGraph(MessagesState)
builder.add_node(chat)
builder.add_edge(START, 'chat')
graph = builder.compile(store=store)

async def main():
    async for message, metadata in graph.astream(
        input={'messages': [{'role':'user', 'content': "I'm hungry."}]},
        stream_mode='messages'
    ):
        print(message.content, end='')

if __name__ == '__main__':
    asyncio.run(main())