# from typing import TypedDict
#
# from langchain_core.messages.utils import (trim_messages, count_tokens_approximately, AnyMessage)
# from langgraph.checkpoint.memory import InMemorySaver
# from langgraph.constants import START
# from langgraph.graph import MessagesState, StateGraph
# from langchain_openai import ChatOpenAI
# import os
#
# from langmem.short_term import SummarizationNode, RunningSummary
#
# model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
#                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0)
# summarization_model = model.bind(max_tokens=1024)
#
# class State(MessagesState):
#     context: dict[str, RunningSummary]
#
# class LLMInputState(TypedDict):
#     summarized_messages: list[AnyMessage]
#     context: dict[str, RunningSummary]
#
# def call_model(state: LLMInputState):
#     response = model.invoke(state['summarized_messages'])
#     return {'messages': [response]}
#
# summarization_node = SummarizationNode(
#     token_counter=count_tokens_approximately,
#     model=summarization_model,
#     max_tokens=256,
#     max_tokens_before_summary=256,
#     max_summary_tokens=128,
# )
#
# checkpointer = InMemorySaver()
# builder = StateGraph(MessagesState)
# builder.add_node(call_model)
# builder.add_node('summarize', summarization_node)
# builder.add_edge(START, 'summarize')
# builder.add_edge('summarize', 'call_model')
# graph = builder.compile(checkpointer=checkpointer)
#
# config = {"configurable": {"thread_id": "1"}}
# graph.invoke({"messages": "hi, my name is bob"}, config)
# graph.invoke({"messages": "write a short poem about cats"}, config)
# graph.invoke({"messages": "now do the same but for dogs"}, config)
# final_response = graph.invoke({"messages": "what's my name?"}, config)
#
# final_response['messages'][-1].pretty_print()
# print('\nSummary:', final_response['context']['running_summary'].summary)

from typing import Any, TypedDict, Optional, Annotated

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage
from langchain_core.messages.utils import count_tokens_approximately
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langmem.short_term import SummarizationNode, RunningSummary

from langchain_openai import ChatOpenAI
import os

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", temperature=0)
summarization_model = model.bind(max_tokens=128)

class State(MessagesState):
    context: Annotated[dict[str, Any], lambda x,y: y if y is not None else x] = {}

class LLMInputState(TypedDict):
    summarized_messages: list[AnyMessage]
    context: dict[str, Any]

summarization_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=summarization_model,
    max_tokens=256,
    max_tokens_before_summary=256,
    max_summary_tokens=128,
)

def call_model(state: LLMInputState):
    response = model.invoke(state["summarized_messages"])
    return {"messages": [response]}

checkpointer = InMemorySaver()
builder = StateGraph(State)
builder.add_node(call_model)
builder.add_node("summarize", summarization_node)
builder.add_edge(START, "summarize")
builder.add_edge("summarize", "call_model")
graph = builder.compile(checkpointer=checkpointer)

# Invoke the graph
config = {"configurable": {"thread_id": "1"}}
# StateSnapshot(values={}, next=(), config={'configurable': {'thread_id': '1'}}, metadata=None, created_at=None, parent_config=None, tasks=(), interrupts=())
print(graph.get_state(config))
graph.invoke({"messages": "hi, my name is bob"}, config)
graph.invoke({"messages": "write a short poem about cats"}, config)
graph.invoke({"messages": "now do the same but for dogs"}, config)
final_response = graph.invoke({"messages": "what's my name?"}, config)

final_response["messages"][-1].pretty_print()
print("Full response keys:", final_response.keys())
print("Context:", final_response.get("context"))

if 'context' in final_response and 'running_summary' in final_response['context']:
    print('\nSummary:', final_response['context']['running_summary'].summary)
else:
    print("\nNo summary available yet")
    print('\nContext keys:', final_response.get('context', {}).keys())

print(list(graph.get_state_history(config)))

thread_id = "1"
checkpointer.delete_thread(thread_id)