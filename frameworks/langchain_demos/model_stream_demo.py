import os
import langchain.chat_models
from langchain_classic.chat_models import init_chat_model
from openai import base_url
import asyncio
from langchain_openai import ChatOpenAI

# model = init_chat_model(model='gpt-5.1', api_key=os.getenv('OPENAI_API_KEY'),
#                         base_url='https://api.chatanywhere.tech')
model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
# Simple streaming
# full = None
# for chunk in model.stream('What color is the sky?'):
#     full = chunk if full is None else full + chunk
#     print(full.text)

# print(full.content_blocks)

# Streaming demo: Streaming events
# async def get_event_stream():
#     async for event in model.astream_events('Hello'):
#         if event['event'] == 'on_chat_model_start':
#             print(f'Input: {event['data']["input"]}')
#         elif event['event'] == 'on_chat_model_stream':
#             print(f'Token: {event['data']["chunk"].text}')
#         elif event['event'] == 'on_chat_model_end':
#             print(f'Full message: {event['data']["output"].text}')
#         else:
#             pass
#
#     asyncio.run(get_event_stream())

# Batching: batch(),batch_as_completed()
list_of_inputs = [
    'What color is the sky?',
    'How do airplanes fly?',
    'What is quantum computing?'
]
# Limit to 5 parallel calls
# responses = model.batch_as_completed(list_of_inputs, config={'max_concurrency': 5})
#
# for resp in responses:
#     print(resp)

# Reasoning demo
# for chunk in model.stream('What is the meaning of life?'):
#     reasoning_steps = [r for r in chunk.content_blocks if r['type'] == 'reasoning']
#     print(reasoning_steps if reasoning_steps else chunk.text)

response = model.invoke("Create a picture of a cat")
print(response.content_blocks)