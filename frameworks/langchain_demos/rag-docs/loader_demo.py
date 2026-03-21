import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

from pymongo import MongoClient

embeddings = DashScopeEmbeddings(model='text-embedding-v3',
                             dashscope_api_key=os.getenv('DASHSCOPE_API_KEY'))

# Only keep post title, headers, and content from the full HTML.
bs4_strainer = bs4.SoupStrainer(class_=('post-title','post-header','post-content'))
loader = WebBaseLoader(
    web_path='https://lilianweng.github.io/posts/2023-06-23-agent/',
    bs_kwargs={'parse_only': bs4_strainer}
)
docs = loader.load()

assert len(docs) == 1
print(f'Total chars: {len(docs[0].page_content)}')
print(docs[0].page_content[:500])

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

all_chunks = []
for doc in docs:
    all_chunks.append(splitter.split_text(doc[0].page_content))

# Vector store of ElasticSearch
from langchain_elasticsearch import ElasticsearchStore
vector_store = ElasticsearchStore(
    index_name='lc-store-1',
    embedding=embeddings,
    es_url='http://localhost:9200'
)
vector_store.add_documents(documents=all_chunks)

# Vector store of Milvus
from langchain_milvus import Milvus
URI = './milvus_demo.db'
vector_store = Milvus(
    embedding_function=embeddings,
    connection_args={'uri': URI},
    index_params={'index_type': 'FLAT', 'metric_type': 'L2'}
)
vector_store.add_documents(documents=all_chunks)

# Vector store of MongoDB
from langchain_mongodb import MongoDBAtlasVectorSearch
MONGODB_URI = "mongodb+srv://user1:123455@localhost:52321/embed_test?retryWrites=true&w=majority"
DATABASE_NAME = 'embed_test'
COLLECTION_NAME = "test_1"
ATLAS_VECTOR_SEARCH_INDEX_NAME = 'vector_index_1'
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

vector_store = MongoDBAtlasVectorSearch(
    embedding=embeddings,
    collection=collection,
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    relevance_score_fn='cosine',
    # Store field name
    text_key='text',
    embedding_key='embedding'
)
vector_store.add_documents(documents=all_chunks)

result_with_score = vector_store.similarity_search_with_score('What is the difference between LLM and GPT?', k = 3)