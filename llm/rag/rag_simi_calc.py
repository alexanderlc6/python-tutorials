import os

from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from numpy import dot
from numpy.linalg import norm

load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.chatanywhere.tech")

# COSINE SIMILARITY
def cos_sim(a, b):
    # More similar when the cosine distance getting bigger
    return dot(a, b) / (norm(a) * norm(b))

# L2 SIMILARITY
def l2(a, b):
    # More similar when the L2 distance getting smaller
    x = np.asarray(a) - np.asarray(b)
    return norm(x)

def get_embeddings(texts, model='text-embedding-3-large'):
    data = client.embeddings.create(input=texts, model=model).data
    print(data)
    return [x.embedding for x in data]

# Question query
query = '国际争端'

documents = [
    "联合国安理会上，俄罗斯与美国，伊朗与以色列“吵“起来了",
    "土耳其、芬兰、瑞典与北约代表将继续就瑞典“入约“问题进行谈判",
    "日本岐阜市陆上自卫队射击场内发生枪击事件3人受伤",
    "孙志刚被判死缓 减为无期徒刑后终身监禁 不得减刑、假释",
    "以色列立法禁联合国机构，美表态担忧，中东局势再生波澜"
]
query_vec = get_embeddings([query])[0]
doc_vecs = get_embeddings(documents)
print('Cosine distance:')
print(cos_sim(query_vec, query_vec))

for vec in doc_vecs:
    print(cos_sim(query_vec, vec))

print('\nEuclidean distance:')
print(l2(query_vec, query_vec))
for vec in doc_vecs:
    print(l2(query_vec, vec))