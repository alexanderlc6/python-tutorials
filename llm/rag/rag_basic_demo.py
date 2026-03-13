from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
# os.putenv('OPENAI_API_KEY', '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')

print(os.getenv('OPENAI_API_KEY'))
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.chatanywhere.tech")
# client = OpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),
#         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def get_embeddings(texts, model = 'text-embedding-3-large'):
    # data = client.chat.completions.create(
    #     model='qwen-max',
    #     messages=[{'role':'user','content':texts}]
    # ).data

    data = client.embeddings.create(model=model, input=texts).data
    print(data)
    return [x.embedding for x in data]

test_query = ['LLM']
vec = get_embeddings(test_query)
# print(vec)
print(vec[0])
print(len(vec[0]))