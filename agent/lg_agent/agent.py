from typing import TypedDict, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_community.tools.tavily_search import TavilySearchResults


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


tools = [TavilySearchResults(max_results = 1)]
tool_node = ToolNode(tools)

def call_llm(state):
    messages = state["messages"]
    messages = [{"role": "system", "content": "你是一个中文智能小助手。"}] + messages
    model = ChatOpenAI(temperature=0, model_name = "gpt-4o-mini")
    model = model.bind_tools(tools)
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]

    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

workflow = StateGraph(AgentState)
workflow.add_node("llm", call_llm)
workflow.add_node("search", tool_node)
workflow.set_entry_point("llm")
workflow.add_conditional_edges(
    "llm",
            should_continue,
{
            "continue": "search",
            "end": END,
         },
)

workflow.add_edge("search", "llm")
graph = workflow.compile()

if  __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print("User: " + user_input)
        if user_input.lower() in["quit", "exit", "q"]:
            print("Goodbye!")
            break

        response = graph.invoke({"messages": [("user", user_input)]})
        print(response["messages"][-1].content)