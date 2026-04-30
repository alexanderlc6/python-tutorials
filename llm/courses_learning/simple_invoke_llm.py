import os
from openai import OpenAI

client = OpenAI(
    # api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
)

completion = client.chat.completions.create(
    model='qwen3-max',
    messages=[
        {'role':'system', 'content': 'You are a helpful assistant.'},
        {'role':'user', 'content': 'Who are you?What can you do?'}
    ],
    stream=True
)

for chunk in completion:
    print(chunk.choices[0].delta.content, end='', flush=True)