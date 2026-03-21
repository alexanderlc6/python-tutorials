import time
from langchain_classic.embeddings import CacheBackedEmbeddings
from langchain_classic.storage import LocalFileStore
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_core.stores import InMemoryByteStore
import os

embeddings = DashScopeEmbeddings(model='text-embedding-v3',
                             dashscope_api_key=os.getenv('DASHSCOPE_API_KEY'))
store = LocalFileStore("./cache")
cached_embedder = CacheBackedEmbeddings.from_bytes_store(
    embeddings,
    store,
    namespace=embeddings.model
)
tic = time.time()
print(cached_embedder.embed_query('Hello Alex'))
print(f'First call tool: {time.time() - tic:2f} seconds.')

# Subsequent calls use the cache
tic = time.time()
print(cached_embedder.embed_query('Hello Alex'))
print(f'Second call tool: {time.time() - tic:2f} seconds.')

# Bytes KV store demo
kv_store = InMemoryByteStore()
kv_store.mset([
        ['k1', b'v1'],
        ['k2', b'v2']
    ]
)
kv_store.mget(
    ['k1', 'k2']
)
# kv_store.mdelete(['k1', 'k2'])