# ReAct RAG Agent demo
from llama_index.core import SimpleDirectoryReader
from dotenv import load_dotenv
from llama_index.core.base.embeddings.base import similarity

load_dotenv()

# Load business dataset
A_docs = SimpleDirectoryReader(input_files=['./A.pdf']).load_data()
B_docs = SimpleDirectoryReader(input_files=['./B.pdf']).load_data()

# Create document index
from llama_index.core import VectorStoreIndex
A_index = VectorStoreIndex.from_documents(A_docs)
B_index = VectorStoreIndex.from_documents(B_docs)

# Persistence for doc index to local storage
from llama_index.core import StorageContext
A_index.storage_context.persist(persist_dir='./storage/A')
B_index.storage_context.persist(persist_dir='./storage/B')

# Read index from local
from llama_index.core import load_index_from_storage
try:
    storage_context = StorageContext.from_defaults(persist_dir='./storage/A')
    A_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(persist_dir='./storage/B')
    B_index = load_index_from_storage(storage_context)
    index_loaded = True
except:
    index_loaded = False

# Create query engine
A_engine = A_index.as_query_engine(similarity_top_k=3)
B_engine = B_index.as_query_engine(similarity_top_k=3)

# Config query tools
from llama_index.core.tools import QueryEngineTool, ToolMetadata
query_engine_tools = [
    QueryEngineTool(
        query_engine=A_engine,
        metadata=ToolMetadata(name="A_fin_data", description="A")
    ),
    QueryEngineTool(
        query_engine=B_engine,
        metadata=ToolMetadata(name="B_fin_data", description="B")
    )
]

# Config LLM
from llama_index.llms.openai import OpenAI
llm = OpenAI(model='gpt-4')

# Create ReAct Agent
from llama_index.core.agent import ReActAgent
agent = ReActAgent.from_tools(query_engine_tools, llm=llm, verbose=True)

# Agent do tasks
print(agent.chat('Compare the sales of the two companies.'))