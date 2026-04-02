import asyncio
from pydoc_data.topics import topics

from langchain.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableMap
from langserve import RemoteRunnable

openai = RemoteRunnable('http://localhost:8900/openai')
# anthropic = RemoteRunnable('http://localhost:8900/anthropic')
qwen = RemoteRunnable('http://localhost:8900/qwen')
joke_chain = RemoteRunnable('http://localhost:8900/joke')

joke_chain.invoke({'topic':'parrots'})
# or use async: await joke_chain.invoke({'topic':'parrots'})

# Supports stream
async def async_talk():
    result = await joke_chain.ainvoke({'topic':'parrots'})
    print('Joke result:', result)

    prompt = [
        SystemMessage(content='Act as either a cat or a parrot.'),
        HumanMessage(content='Hello!')
    ]
    print('\nStreaming response:')
    async for msg in qwen.astream(prompt):
        print(msg, end='', flush=True)

asyncio.run(async_talk())

prompt = ChatPromptTemplate.from_messages(
    [('system', 'Tell me a long story about {topic}')]
)
chain = prompt | RunnableMap({
    # 'openai': openai,
    'qwen': qwen
})

async def async_batch_tell():
    topics = ['parrots', 'cats', 'dogs']
    batch_results = await chain.abatch([{'topic': t} for t in topics])
    for topic, result in zip(topics, batch_results):
        print(f'\n------ {topic} ------')
        print('Batch results:', batch_results)

asyncio.run(async_batch_tell())