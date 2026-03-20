from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import DashScopeEmbeddings
import os

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = DashScopeEmbeddings(model='text-embedding-v3',
                             dashscope_api_key=os.getenv('DASHSCOPE_API_KEY'))
vector_store = InMemoryVectorStore(embeddings)

# Add documents content
documents = [
    Document(
        page_content="Nike operates 9 distribution centers across the United States.",
        metadata={"source": "Nike annual report", "topic": "logistics"}
    ),
    Document(
        page_content="Nike's largest distribution center is located in Memphis, Tennessee.",
        metadata={"source": "logistics doc", "topic": "warehouse"}
    ),
    Document(
        page_content="The company has invested heavily in automated distribution systems.",
        metadata={"source": "tech report", "topic": "automation"}
    )
]
vector_store.add_documents(documents=documents, ids=['doc1','doc2','doc3'])

    # Load from webpage
    # loader = WebBaseLoader("https://about.nike.com/en/impact/reporting/our-operations")
    # docs = loader.load()
    # splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    # chunks = splitter.split_documents(docs)
    # vector_store.add_documents(documents=chunks)

# Direct Search
# results = vector_store.similarity_search('How many distribution centers does Nike have in the US?', k=2)
#
# # Async query
# # results = async vector_store.similarity_search('How many distribution centers does Nike have in the US?')
# if results:
#     print(f'Found {len(results)} documents')
#     for i, doc in enumerate(results):
#         print(f'Document {i}:')
#         print(f'Content: {doc.page_content}')
#         print(f'Metadata: {doc.metadata}')
# else:
#     print('No documents found.')

# Search with scores
results = vector_store.similarity_search_with_score("What was Nike's revenue in 2023?")
doc, score = results[0]
print(f'Score:{score}\n')
print(doc)

# Return documents based on similarity to an embedded query
embedding = embeddings.embed_query("How were Nike's margins impacted in 2023?")
results = vector_store.similarity_search_by_vector(embedding)
print(results[0])

# Indexing and retrieval
text1 = "LangChain is the framework for building context-aware reasoning applications"
text2 = "LangGraph is a library for building stateful, multi-actor applications with LLMs"
vec_store = InMemoryVectorStore.from_texts([text1, text2], embedding=embeddings)
# VectorStoreRetriever
retriever = vec_store.as_retriever()
# Retrieve the most similar text
retrieved_docs = retriever.invoke('What is LangChain?')
print(retrieved_docs[0].page_content)

single_vector = embeddings.embed_query(text1)
print(str(single_vector[:100]))

two_vectors = embeddings.embed_documents([text1, text2])
for vec in two_vectors:
    print(str(vec)[:100])

from typing import List
from langchain_core.runnables import chain

# @chain
# def receiver(query: str) -> List[Document]:
#     return vec_store.similarity_search(query,k=1)
# Or:
retriever = vec_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 1},
)
result = retriever.batch(
    [
        "How many distribution centers does Nike have in the US?",
        "When was Nike incorporated?",
    ]
)

import mlflow
mlflow.openai.autolog()
with mlflow.start_run():
    mlflow.log_dict({
        'retrieved_doc0-page_content': retrieved_docs[0].page_content,
        'receiver-result': result
    },
    artifact_file='retrieved_docs.json',
    )