from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.redis import RedisSaver
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

# Use Redis
DB_URI = 'redis://localhost:6379'

# with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
# with MongoDBSaver.from_conn_string(DB_URI) as checkpointer:
with RedisSaver.from_conn_string(DB_URI) as checkpointer:
    # checkpointer.setup()

    def call_model(state: MessagesState):
        response = model.invoke(state['messages'])
        return {'messages': response}

    builder = StateGraph(MessagesState)
    builder.add_node('call_model', call_model)
    builder.add_edge(START, 'call_model')
    # builder.add_edge('call_model', END)
    graph = builder.compile(checkpointer=checkpointer)

    # Use graph
    config = {
        'configurable': {
            'thread_id': '1',
            # Specify history checkpoint to recover the talk session
            # 'checkpoint_id': '1f121b0a-4bc1-64f2-8010-49db5b192fb4'
        },

    }

    # Sync mode
    # # First round talk
    # response = graph.invoke({'messages': [{'role': 'user', 'content': "Hi!I'm Alex"}]}, config)
    # print(response['messages'][-1].content)
    #
    # # Second round talk: the model can remember the user's name
    # response = graph.invoke({'messages': [{'role': 'user', 'content': "What's my name?"}]}, config)
    # print(response['messages'][-1].content)

    # Async mode
    for chunk in graph.stream(
            {'messages': [{'role': 'user', 'content': "Hi!I'm Alex"}]},
                    config,
                    stream_mode='values'
                  ):
        chunk['messages'][-1].pretty_print()
    # Output:
    # ================================ Human Message =================================
    #
    # hi! I'm bob
    # ================================== Ai Message ==================================
    #
    # Hello Bob! It's nice to meet you. Is there anything specific you'd like to talk about or any questions you have?

    for chunk in graph.stream(
            {'messages': [{'role': 'user', 'content': "What's my name?"}]},
            config,
            stream_mode='values'
    ):
        chunk['messages'][-1].pretty_print()
    # Output:
    # ================================ Human Message =================================
    #
    # what's my name?
    # ================================== Ai Message ==================================
    #
    # Your name is Bob! Is there anything else you'd like to chat about or any other questions you have?


    # Query history records
    history = checkpointer.list(config)
    for chp in history:
        print(f"Checkpoint ID:{chp.checkpoint['id']}")
        print(f"Parent ID:{chp.checkpoint.get('parent_id')}")
        print(f'Channel values:{chp.checkpoint.get('channel_values', {})}')
        print('---')
    print(f'{len(list(history))} checkpoints stored in total.')

    # Query specific checkpoint
    checkpoint = checkpointer.get(config)