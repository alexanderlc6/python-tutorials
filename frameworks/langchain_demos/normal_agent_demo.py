from typing import Literal, Any

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_agent, HumanInTheLoopMiddleware
from langchain_core.messages import SystemMessage, HumanMessage, AIMessageChunk, AnyMessage, AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
import os

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langgraph.types import Interrupt, Command
from pydantic import BaseModel

from frameworks.langchain_demos.langgraph.langgraph_subgraph_demo import checkpointer


def get_weather(city:str) -> str:
    '''Test tool function'''
    return f"It's sunny in {city}"

model = ChatOpenAI(
    api_key=os.getenv('DASHSCOPE_API_KEY'),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model='qwen-max',
    temperature=0.1,
    max_tokens=1000,
    timeout=30
)

# Streaming from sub-agents
def call_weather_agent(query: str) -> str:
    """Query the weather agent."""
    result = weather_agent.invoke(
        {'messages': [{'role': 'user', 'content': query}]}
    )
    return result['messages'][-1].text

weather_agent = create_agent(
    name='weather_agent',
    model = model,
    tools=[get_weather]
)

# Run the agent
res = weather_agent.invoke(
    { 'messages': [{ 'role': 'user', 'content': 'what is the weather in SF?'}]
    })
# res = agent.invoke({'message': [{'role':'user', 'content': 'what is the weather in sf'}]})
print(res)

def _render_message_chunk(token: AIMessageChunk) -> None:
    if token.text:
        print(token.text, end='|')
    if token.tool_call_chunks:
        print(token.tool_call_chunks)

def _render_completed_message(message: AnyMessage) -> None:
    if isinstance(message, AIMessage) and message.tool_calls:
        print(f'Tool calls: {message.tool_calls}')
    if isinstance(message, ToolMessage):
        print(f'Tool response: {message.content_blocks}')


for chunk in weather_agent.stream(
        {'messages': [{'role':'user', 'content': 'what is the weather in SF'}]},
        # Get stream response all values output
        # stream_mode='values',
        # Get stream response update increment info
        # stream_mode='updates',
        # Set stream_response mode='messages' to output LLM tokens
        stream_mode=['messages', 'updates'],
        version='v2'
    ):
    if chunk['type'] == 'updates':
        for step_source, update_data in chunk['data'].items():
            print(f'step: {step_source}')
            # print(f'content: {update_data['messages'][-1].content_blocks}')
            if step_source in ('model', 'tools'):
                _render_completed_message(update_data['messages'][-1])

    if chunk['type'] == 'messages':
        token, metadata = chunk['data']
        print(f"node: {metadata['langgraph_node']}")
        print(f'content: {token.content_blocks}')
        print('\n')
        if isinstance(token, AIMessageChunk):
            _render_message_chunk(token)
    # Output:
    # node: model
    # content: [
    #     {'type': 'tool_call_chunk', 'id': 'call_641d7a1dc6dc46ce97118f', 'name': 'get_weather', 'args': '{"city": "SF',
    #      'index': 0}]
    #
    # node: model
    # content: [{'type': 'tool_call_chunk', 'id': '', 'name': None, 'args': '"}', 'index': 0}]
    #
    # node: model
    # content: []
    #
    # node: model
    # content: []
    #
    # node: tools
    # content: [{'type': 'text', 'text': "It's sunny in SF"}]
    #
    # node: model
    # content: [{'type': 'text', 'text': 'The weather in'}]
    #
    # node: model
    # content: [{'type': 'text', 'text': ' SF is sunny'}]
    #
    # node: model
    # content: [{'type': 'text', 'text': '.'}]
    #
    # node: model
    # content: []
    #
    # node: model
    # content: []

# Custom stream mode: To stream updates from tools as they are executed
from langgraph.config import get_stream_writer
def get_weather_write(city: str) -> str:
    """Get weather for a given city."""
    writer = get_stream_writer()
    # stream any arbitrary data
    writer(f"Looking up data for city: {city}")
    writer(f"Acquired data for city: {city}")
    return f"It's always sunny in {city}!"

agent = create_agent(
    model=model,
    tools=[get_weather_write, call_weather_agent],
    system_prompt='You are a helpful assistant',
    name="supervisor"
)

current_agent = None
for chunk in agent.stream(
        {'messages': [{'role':'user', 'content': 'what is the weather in SF'}]},
        # stream_mode='custom',
        # Get multiple stream response mode output
        stream_mode=['messages', 'update', 'custom'],
        version='v2',
        subgraphs=True
    ):
    if chunk['type'] == 'custom':
        print(chunk['data'])
        # print(f'Tool calls: {chunk['data'].tool_calls}')
    # Output:
    # Looking up data for city: SF
    # Acquired data for city: SF

    if chunk["type"] == "messages":
        token, metadata = chunk["data"]
        if agent_name := metadata.get('lc_agent_name'):
            if agent_name != current_agent:
                print(f'{agent_name}:')
                current_agent = agent_name
    # Get multiple stream response mode output
    print(f'stream mode:{chunk["type"]}')
    print(f'content: {chunk["data"]}')
    print('\n')

# Accessing completed messages
from langgraph.config import get_stream_writer
class ResponseSafety(BaseModel):
    evaluation: Literal['safe', 'unsafe']

@after_agent(can_jump_to=['end'])
def safety_guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Model-based guardrail: Use an LLM to evaluate response safety."""
    stream_writer = get_stream_writer()
    # Get the model response
    if not state['messages']:
        return None

    last_message = state['messages'][-1]
    if not isinstance(last_message, AIMessage):
        return None

    # Use another model to evaluate safety
    model_with_tools = model.bind_tools([ResponseSafety], tool_choice='any')
    result = model_with_tools.invoke(
        [
            {
                'role': 'system',
                'content': 'Evaluate this AI response as generally safe or unsafe.'
            },
            {
                'role': 'user',
                'content': f'AI response: {last_message.text}'
            }
        ]
    )
    stream_writer(result)
    tool_call = result.tool_calls[0]
    if tool_call['args']['evaluation'] == 'unsafe':
        last_message.content = 'I cannot provide that response. Please rephrase your request.'

    return None

checkpointer = InMemorySaver()

# Streaming with human-in-the-loop
def _render_interrupt(interrupt: Interrupt) -> None:
    interrupts = interrupt.value
    for request in interrupts['action_requests']:
        print(request['description'])

# Collect a decision for each interrupt, edit one tool call and accept the other
def _get_interrupt_decisions(interrupt: Interrupt) -> list[dict]:
    return [
        {
            'type': 'edit',
            'edited_action': {
                'name': 'get_weather',
                # Human-in-the-Loop action: Override when found [boston] in request body
                'args': {'city': 'Boston, US'}
            }
        }
        if 'boston' in request['description'].lower()

        else {'type': 'approve'}
        for request in interrupt.value['action_requests']
    ]

config = {'configurable': {'thread_id': '123'}}

# for chunk in model.stream('Why do parrots have colorful feathers?'):
#     reasoning_steps = [r for r in chunk.content_blocks if r['type'] == 'reasoning']
#     print(reasoning_steps if reasoning_steps else chunk.text)
agent: Runnable = create_agent(
    model=model,
    tools=[get_weather],
    middleware=[
        safety_guardrail,
        # Streaming with human-in-the-loop
        HumanInTheLoopMiddleware(interrupt_on={'get_weather': True})],
    checkpointer = checkpointer
)

for chunk in agent.stream(
  {'messages': [{'role':'user', 'content': 'Can you look up the weather in Boston and San Francisco?'}]},
        stream_mode=['messages', 'updates'],
        version='v2'
):
    if chunk['type'] == 'messages':
        token, metadata = chunk['data']
        if not isinstance(token, AIMessageChunk):
            continue

        reasoning = [b for b in token.content_blocks if b['type'] == 'reasoning']
        text = [b for b in token.content_blocks if b['type'] == 'text']
        if reasoning:
            print(f'[thinking]: {reasoning[0]['reasoning']}', end='')
        elif text:
            print(text[0]['text'], end='')

# =====Human-in-the-Loop demo====================
# Render completed message with interruption
# Streaming with human-in-the-loop
interrupts = []
decisions = []
for interrupt in interrupts:
    decisions[interrupt.id] = {
        'decisions': _get_interrupt_decisions(interrupt)
    }

print(decisions)

for chunk in agent.stream(
        # Execute decision when interrupted and execute command
        Command(resume=decisions),
        {'messages': [{'role': 'user', 'content': 'what is the weather in SF'}]},
        stream_mode=['messages', 'updates'],
        version='v2',
        config=config
):
    if chunk['type'] == 'updates':
        for source, update_data in chunk['data'].items():
            if source in ("model", "tools"):
                _render_completed_message(update_data["messages"][-1])
            if source == "__interrupt__":
                interrupts.extend(update_data)
            _render_interrupt(update_data[0])

