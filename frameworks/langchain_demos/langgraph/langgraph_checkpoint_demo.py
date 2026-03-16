from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
import os

# Use checkpointer stored in DB
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.mongodb import MongoDBSaver

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0)
# Use Postgresql
DB_URI = 'postgresql://postgres:postgres@localhost:5432/postgres?sslmode=disable'

# Use MongoDB
DB_URI = 'mongodb://localhost:27017'

# with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
    # checkpointer.setup()

    def call_model(state: MessagesState):
        response = model.invoke(state['messages'])
        return {'messages': response}

    builder = StateGraph(MessagesState)
    builder.add_node('call_model', call_model)
    builder.add_edge(START, 'call_model')
    builder.add_edge('call_model', END)
    graph = builder.compile(checkpointer=checkpointer)

    # Use graph
    config = {'configurable': {'thread_id': '1'}}

    # First round talk
    response = graph.invoke({'messages': [{'role': 'user', 'content': "Hi!I'm Alex"}]}, config)
    print(response['messages'][-1].content)

    # Second round talk: the model can remember the user's name
    response = graph.invoke({'messages': [{'role': 'user', 'content': "What's my name?"}]}, config)
    print(response['messages'][-1].content)

    # Query history records
    history = list(checkpointer.list(config))
    print(f'{len(history)} checkpoints stored in total.')

    # Query specific checkpoint
    checkpoint = checkpointer.get(config)