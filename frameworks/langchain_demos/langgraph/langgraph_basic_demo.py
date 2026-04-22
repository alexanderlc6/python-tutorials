from langgraph.graph import StateGraph, MessagesState, START, END, add_messages
from typing import TypedDict
import operator

def mock_llm(state: MessagesState):
    return {'messages': [{'role': 'ai', 'content': 'hello world'}]}

def plain_node1(state: State):
    return state

def plain_node2(state: State):
    return state

def route_func(a, b):
    return (a + b) > 10


graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_node(plain_node1)
graph.add_node(plain_node2)

graph.add_edge(START, 'mock_llm')
# Add conditional edges
# graph.add_conditional_edges(START, route_func(12, 4), {True: 'plain_node1', False: 'plain_node2'})

graph.add_edge('mock_llm', END)
graph = graph.compile()

print(graph.invoke({'messages': [{'role': 'user', 'content': 'hi'}]}))

from langchain_core.messages import AIMessage, HumanMessage

msg1 = [HumanMessage(content='Hello', id = '1')]
msg2 = [AIMessage(content='hi there', id = '2')]
msg3 = [HumanMessage(content='Hi God', id = '1')]
# [HumanMessage(content='Hello', additional_kwargs={}, response_metadata={}, id='1'), AIMessage(content='hi there', additional_kwargs={}, response_metadata={}, id='2', tool_calls=[], invalid_tool_calls=[])]
print(add_messages(msg1, msg2))
# Override message
# [HumanMessage(content='Hi God', additional_kwargs={}, response_metadata={}, id='1')]
print(add_messages(msg1, msg3))


# Define reducer
from typing import Annotated, TypedDict
from typing_extensions import TypedDict
from operator import add

class State(TypedDict):
    foo: int
    # State would then be {"foo": 2, "bar": ["hi", "bye"]}
    bar: Annotated[list[str], add]

    # add_messages() will deserialize messages into LangChain Message objects whenever a state update is received on the messages channel.
    # Use default message format
    messages: Annotated[list, add_messages]

    # Use OpenAI message format
    messages: Annotated[list, add_messages(format ='langchain-openai')]

def chatbot_node(state: State) -> list:
    return {
        'messages': [
            {'role': 'user', 'content': [
                {'type': 'text', 'text': "Here's an image", 'cache_control': {'type':'ephemeral'}},
                {'type': 'image', 'source': { 'type': 'base64', 'media_type': 'image/jpeg', 'data':'1234'}}
            ]}
        ]
    }

builder = StateGraph(State)
# builder.add_node('chatbot', lambda state: {'messages': [('assistant', 'Hello1')]})
builder.add_node('chatbot', chatbot_node)
builder.set_entry_point('chatbot')
builder.set_finish_point('chatbot')
graph = builder.compile()
# Default message format result: {'bar': [], 'messages': [AIMessage(content='Hello', additional_kwargs={}, response_metadata={}, id='bf84a015-4dcb-42c6-96d7-4e394bfcd7ee', tool_calls=[], invalid_tool_calls=[])]}
print(graph.invoke({}))

# OpenAI message format result:
# {'bar': [], 'messages': [HumanMessage(content=[{'type': 'text', 'text': "Here's an image"}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,1234'}}], additional_kwargs={}, response_metadata={})]}
print(graph.invoke({'messages':[]}))