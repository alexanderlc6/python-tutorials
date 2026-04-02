from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatAnthropic, ChatOpenAI
from langserve import add_routes
import os

app = FastAPI(
    title='LangChain server',
    version=1.0,
    description='A simple server for LangChain Runnable interfaces',
)

add_routes(
    app,
    ChatOpenAI(model='gpt-5.1', api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.chatanywhere.tech", temperature=0, verbose=True),
    path='/openai'
)

# add_routes(
#     app,
#     ChatAnthropic(model='claude-3-5-turbo', temperature=0, verbose=True),
#     path='/anthropic'
# )

add_routes(
    app,
    ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"),
    path='/qwen'
)

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
prompt = ChatPromptTemplate.from_template("Please tell me a joke about {topic}")
add_routes(
    app,
    prompt | model,
    path='/joke'
)

if __name__=='__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8900)