import os
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"), base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def generate_responses(prompt, model='qwen-plus'):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.7,
        # max_tokens=1024,
    )

    return response.choices[0].message.content

"""
prompt = f'''
根据下面的上下文回答问题，保证答案简短且准确，如果不确定答案，请回答“不确定答案”。
New York is a state in the northeastern region of the United States. It is known for its diverse geography, which includes major urban areas like New York City, as well as more rural and natural landscapes such as the Adirondack Mountains, the Finger Lakes, and Niagara Falls. When people refer to "New York," they often mean New York City, which is located at the southern tip of the state, along the Atlantic coast. New York City is one of the largest and most famous cities in the world, comprising five boroughs: Manhattan, Brooklyn, Queens, The Bronx, and Staten Island.

问题：Manhattan是在世界的哪个地方？
'''

# prompt = f'问题：Manhattan是在世界的哪个地方？'
response = generate_responses(prompt)
print(response)

# Define structure and vars
instruction = f'根据下面的上下文回答问题，保证答案简短且准确，如果不确定答案，请回答“不确定答案”。'
context = 'New York is a state in the northeastern region of the United States. It is known for its diverse geography, which includes major urban areas like New York City, as well as more rural and natural landscapes such as the Adirondack Mountains, the Finger Lakes, and Niagara Falls. When people refer to "New York," they often mean New York City, which is located at the southern tip of the state, along the Atlantic coast. New York City is one of the largest and most famous cities in the world, comprising five boroughs: Manhattan, Brooklyn, Queens, The Bronx, and Staten Island.'
# Question description
query = '''
Shanghai是在世界的哪个地方？
'''
prompt = f'''
{instruction}
{context}
{query}
'''

response = generate_responses(prompt)
print(response)

# Demo2: output with JSON format
instruction = '''
根据下面的上下文回答问题，保证答案简短且准确，如果不确定答案，请回答“不确定答案”。
以JSON格式输出：
{"具体问题":"答案"},
'''

examples = '''
{"Who are you?":"I am Alex."}
'''

context = 'New York is a state in the northeastern region of the United States. It is known for its diverse geography, which includes major urban areas like New York City, as well as more rural and natural landscapes such as the Adirondack Mountains, the Finger Lakes, and Niagara Falls. When people refer to "New York," they often mean New York City, which is located at the southern tip of the state, along the Atlantic coast. New York City is one of the largest and most famous cities in the world, comprising five boroughs: Manhattan, Brooklyn, Queens, The Bronx, and Staten Island.'
query = '''
Manhattan是在世界的哪个地方？
'''

prompt = f'''
{instruction}
{context}
{query}
{examples}
'''

response = generate_responses(prompt)
print(response)
"""

# Demo3: Sentiment classification
# prompt = '''
# 将文本分类为中性、负面或正面。
# 文本：明天要放假了，要做家务了啊，好烦啊。
# 情感：
# '''

# response = generate_responses(prompt)
# print(response)

# Demo4: Make sentences by imitating
# prompt = '''
# whatpu is a kind of animal.一个使用whatpu这个词的句子是：我们在非洲玩的时候看到好多可爱的whatpu。
# "faddle"是指快速跳上跳下，一个使用faddle这个词的句子的例子是：
# '''

# prompt = '''
# "调优"本身是一个词语，但是有的人喜欢拆这个词的意思去造句，比如:妈妈的音调优于白鹿。
# 请仿照例子，使用"开心"造句。
# '''
# response = generate_responses(prompt)
# print(response)

# Demo5: Math problem reasoning with sample remind
# prompt = '''
# 这组数字中的奇数加在一起是个偶数：8、9、15、4、12、1、2，
# A: 答案是False
# 这组数字中的奇数加在一起是个偶数：16、11、14、13、24、4、8，
# A: 答案是True
#
# 这组数中的奇数加在一起是个偶数：15、32、5、82、13、1、7，
# A:
# '''
# response = generate_responses(prompt)
# print(response)

# Demo6: Ask with CoT(Thought of Chain) -> answer by steps
prompt = '''
小明有20个苹果，吃了两个，又买了5个，小明现在一共有多少苹果，通过思维链CoT的式来分
析
'''
response = generate_responses(prompt)
print(response)