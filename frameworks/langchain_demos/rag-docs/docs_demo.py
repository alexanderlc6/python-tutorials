import os

import requests
from langchain_core.documents import Document
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.document_loaders import WebBaseLoader, FileSystemBlobLoader
import nest_asyncio
from langchain_unstructured import UnstructuredLoader
from unstructured.cleaners.core import clean_extra_whitespace
from unstructured_client import UnstructuredClient
from unstructured_client.utils import BackoffStrategy, RetryConfig

# documents = [
#     Document(
#         page_content='Dogs are great companions, known for their loyalty and friendliness.',
#         metadata={'source': 'mammal-pets-doc'}
#     ),
#     Document(
#         page_content='Cats are independent pets that often enjoy their own space.',
#         metadata={'source': 'mammal-pets-doc'}
#     )
# ]

# CSV loader
# csv_loader = CSVLoader()
#
# documents = csv_loader.load()
# # For large datasets, lazily load documents
# for doc in csv_loader.lazy_load():
#     print(doc)

# nest_asyncio.apply()

# Web page loader
# webpage_loader = WebBaseLoader(['https://youdao.com/', 'http://www.baidu.com'],
#                                # proxies={'http': 'http://127.0.0.1:7890'},
#                                requests_kwargs={'verify': False}, requests_per_second=1)
# docs = webpage_loader.load()
# print(docs[0])
# print(docs[0].metadata)
# {'source': 'https://www.github.com', 'title': 'GitHub · Change is constant. GitHub keeps you ahead. · GitHub', 'description': "Join the world's most widely adopted, AI-powered developer platform where millions of developers, businesses, and the largest open source community build software that advances humanity.", 'language': 'en'}

# docs = webpage_loader.load()
# print(docs)

# Load a sitemap file
# sitemap_loader = WebBaseLoader(['https://www.govinfo.gov/content/pkg/CFR-2018-title10-vol3/xml/CFR-2018-title10-vol3-sec431-86.xml'])
# sitemap_loader.default_parser='xml'
# docs = sitemap_loader.load()
# print(docs)

# Lazy loading: load one page at a time in order to minimize memory requirements.
# pages = []
# for doc in webpage_loader.lazy_load():
#     pages.append(doc)
#
# # async for doc in webpage_loader.alazy_load():
# #     pages.append(docs)
#
# print(pages[0].page_content[:100])
# print(pages[0].metadata)

# Load unstructured documents
file_paths = [
    './example-docs/Integration Process Intro.pdf',
    './example-docs/log-data.txt'
]

# client = UnstructuredClient(api_key_auth=os.getenv('UNSTRUCTURED_API_KEY'),
#                             # client=requests.Session(),
#                             server_url='https://api.unstructuredapp.io/general/v0/general',
#                             retry_config=RetryConfig(
#                                 strategy='backoff',
#                                 retry_connection_errors=True,
#                                 backoff=BackoffStrategy(
#                                   initial_interval=500,
#                                     max_interval=60000,
#                                     exponent=1.5,
#                                     max_elapsed_time=900000
#                                 ))
#                             )

# Use unstructured client
# unstructured_loader = UnstructuredLoader(file_paths,
#                                          # api_key=os.getenv('UNSTRUCTURED_API_KEY'),   # Do not need when passing [client] object
#                                          partition_via_api=True,
#                                          client=client,
#                                          post_processors=[clean_extra_whitespace],
#                                          split_pdf_page=True,
#                                          split_pdf_page_range=[1,10],
#                                          chunking_strategy="basic",
#                                          max_characters=1000000,
#                                          include_orig_elements=False,
#                                         )
#
#
# unstructured_docs = unstructured_loader.load()
# print(unstructured_docs[0])
# print(unstructured_docs[0].metadata)
# print(unstructured_docs[0].metadata['filename'], ':', unstructured_docs[0].page_content[:100])
# print("Number of LangChain documents:", len(unstructured_docs))
# print("Length of text in the document:", len(unstructured_docs[0].page_content))
# print(unstructured_docs[5:10])

# Async mode for unstructured_loader
# pages = []
# for doc in unstructured_loader.lazy_load():
#     pages.append(doc)

# Load webpage with unstructured_loader
# unstructured_loader = UnstructuredLoader(web_url='http://www.sina.com.cn', requests_kwargs={'verify': False})
# unstructured_docs = unstructured_loader.load()
# for doc in unstructured_docs:
#     print(f"{doc}\n")

# Use pyPDF to load pdf documents
from langchain_community.document_loaders import PyPDFLoader
pdf_file_path = './example-docs/Integration Process Intro.pdf'
pdf_loader = PyPDFLoader(pdf_file_path)
pdf_doc = pdf_loader.load()
# print(pdf_doc[0])

import pprint
# pprint.pp(pdf_doc[0].metadata)
# {'producer': 'Microsoft® Word a Microsoft 365-höz',
#  'creator': 'Microsoft® Word a Microsoft 365-höz',
#  'creationdate': '2026-01-28T14:59:00+01:00',
#  'title': 'Integration process and testing',
#  'author': 'Brautigam Sándor',
#  'moddate': '2026-01-28T14:59:00+01:00',
#  'source': './example-docs/Integration Process Intro.pdf',
#  'total_pages': 39,
#  'page': 0,youdao
#  'page_label': '1'}

# pyPDF lazy load
pages = []
all_pages = []
for doc in pdf_loader.lazy_load():
    pages.append(doc)
    all_pages.append(doc)

    if(len(pages) >= 10):
        # do some paged operation, e.g. index.upsert(page)
        ...
        # Clear current batch pages
        pages = []

if pages:
    # do some paged operation for last < 10 pages, e.g. index.upsert(page)
    ...

# print('Total pages:', len(pages))
# print(all_pages[0].page_content[:100]) # First 100 chars of the first page
# Integration process and testing v1.24
# 31
# 6.6.4.1 Testing
# The MDAPI module is responsible for handl
# pprint.pp(pages[0].metadata)
# {'producer': 'Microsoft® Word a Microsoft 365-höz',
#  'creator': 'Microsoft® Word a Microsoft 365-höz',
#  'creationdate': '2026-01-28T14:59:00+01:00',
#  'title': 'Integration process and testing',
#  'author': 'Brautigam Sándor',
#  'moddate': '2026-01-28T14:59:00+01:00',
#  'source': './example-docs/Integration Process Intro.pdf',
#  'total_pages': 39,
#  'page': 30,
#  'page_label': '31'}

pdf_loader = PyPDFLoader(pdf_file_path,
                         # Extract the PDF by page. each page is extracted as a langchain document object
                         # mode='page'
                         # Extract the whole PDF as a single langchain document object
                         mode='single',
                         pages_delimiter="\n-------THIS IS A CUSTOM END OF PAGE-------\n",
                         )
pdf_doc = pdf_loader.load()
# print(len(pdf_doc))
# pprint.pp(pdf_doc[0].metadata)
# Extract the PDF by page. each page is extracted as a langchain document object
# 39
# {'producer': 'Microsoft® Word a Microsoft 365-höz',
#  'creator': 'Microsoft® Word a Microsoft 365-höz',
#  'creationdate': '2026-01-28T14:59:00+01:00',
#  'title': 'Integration process and testing',
#  'author': 'Brautigam Sándor',
#  'moddate': '2026-01-28T14:59:00+01:00',
#  'source': './example-docs/Integration Process Intro.pdf',
#  'total_pages': 39,
#  'page': 0,
#  'page_label': '1'}

# Extract the whole PDF as a single langchain document object
# 1
# {'producer': 'Microsoft® Word a Microsoft 365-höz',
#  'creator': 'Microsoft® Word a Microsoft 365-höz',
#  'creationdate': '2026-01-28T14:59:00+01:00',
#  'title': 'Integration process and testing',
#  'author': 'Brautigam Sándor',
#  'moddate': '2026-01-28T14:59:00+01:00',
#  'source': './example-docs/Integration Process Intro.pdf',
#  'total_pages': 39}

# pprint.pp(pdf_doc[0].metadata[:1000])

# Parse images in pdf document
from langchain_community.document_loaders.parsers import LLMImageBlobParser, PyPDFParser
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()
model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

pdf_img_loader = PyPDFLoader(pdf_file_path,
                            mode='page',
                             # images_inner_format='markdown-img',
                             # images_parser=RapidOCRBlobParser(),

                             # images_inner_format='html-img',
                             # images_parser=TesseractBlobParser(),

                             images_inner_format='markdown-img',
                             images_parser=LLMImageBlobParser(model=model,),
                            )
pdf_img_doc = pdf_img_loader.load()
print(pdf_img_doc[5].page_content)

# Pares pdf file
from langchain_community.document_loaders.generic import GenericLoader
parse_pdf_loader = GenericLoader(
    blob_loader=FileSystemBlobLoader(
        path='./example-docs',
        # url="s3://mybucket",    # Support OSS URL document
        glob='*.pdf',
    ),
    blob_parser=PyPDFParser()
)
parse_pdf_docs = parse_pdf_loader.load()
print(parse_pdf_docs[0].page_content)
pprint.pp(parse_pdf_docs[0].metadata)

# Split by chunk blocks
from langchain_text_splitters import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True
)

# Embedding demo
all_splits = text_splitter.split_documents(parse_pdf_docs)
print(len(all_splits))  # 72

from langchain_openai import OpenAIEmbeddings
import os

embeddings = OpenAIEmbeddings(model='text-embedding-3-large',
                              api_key=os.getenv('OPENAI_API_KEY'),
                              base_url="https://api.chatanywhere.tech"
                              )
vector1 = embeddings.embed_query(all_splits[0].page_content)
vector2 = embeddings.embed_query(all_splits[1].page_content)

assert len(vector1) == len(vector2)
print(f'Generated vectors of length {len(vector1)}\n')
print(vector1[:10])
# Generated vectors of length 3072
#
# [-0.03107789158821106, 0.010468140244483948, -0.014991529285907745, 0.024009495973587036, 0.009195636957883835, -0.014866679906845093, -0.03682096302509308, 0.06891685724258423, -0.027658939361572266, 0.010737046599388123]

# Computing cosine similarity between two vectors
# import numpy as np
# def cosine_similarity(vec1, vec2):
#     dot = np.dot(vec1, vec2)
#     return dot / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
#
# similarity = consine_similarity(query_embedding, document_embedding)
# print('Cosine Similarity:', similarity)

from langchain_core.vectorstores import InMemoryVectorStore
vector_store = InMemoryVectorStore(embeddings)
ids = vector_store.add_documents(documents=all_splits)

# Text splitter by JSON format
import json
import requests
from langchain_text_splitters import RecursiveJsonSplitter
json_data = requests.get('https://api.smith.langchain.com/openapi.json').json()
splitter = RecursiveJsonSplitter(max_chunk_size=300)
json_chunks = splitter.split_json(json_data=json_data)
for chunk in json_chunks[:3]:
    print(chunk)

# The splitter can also output documents
docs = splitter.create_documents(texts=[json_data])
for doc in docs[:3]:
    print(doc)

# Obtain string content directly(use convert_lists to limit chuck size)
texts = splitter.split_text(json_data=json_data, convert_lists= True)
print(texts[0])
print(texts[1])
print((len(text) for text in texts))
print()
print(texts[3])
print(texts[1])
# {"paths": {"/api/v1/sessions/{session_id}": {"get": {"tags": {"0": "tracer-sessions"}, "summary": "Read Tracer Session", "description": "Get a specific session.", "operationId": "read_tracer_session_api_v1_sessions__session_id__get"}}}}
print(doc[1])
# Document(page_content='{"paths": {"/api/v1/sessions/{session_id}": {"get": {"tags": ["tracer-sessions"], "summary": "Read Tracer Session", "description": "Get a specific session.", "operationId": "read_tracer_session_api_v1_sessions__session_id__get"}}}}')