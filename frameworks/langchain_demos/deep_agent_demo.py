from deepagents import create_deep_agent

def get_weather(city:str) -> str:
    return f"It's sunny in {city}"

agent = create_deep_agent(
    tools=[get_weather],
    system_prompt='You are a helpful assistant'
)

# Run the agent
res = agent.invoke(
    {'message': [{'role':'user', 'content': 'what is the weather in sf'}]}
)
print(res.items())