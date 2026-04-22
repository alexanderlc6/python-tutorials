# Install package: pip install -qU  langchain-community dashscope
# from getpass import getpass
# DASHSCOPE_API_KEY = getpass()

import os
# os.environ['DASHSCOPE_API_KEY'] = DASHSCOPE_API_KEY

from langchain_community.llms import Tongyi
from langchain_core.prompts import PromptTemplate

llm = Tongyi()
template = """Question: {question}
Answer: Let's think step by step."""

prompt = PromptTemplate.from_template(template)
chain = prompt | llm

question = 'What the NBA Lakers team won in the year of iphone 8 published on the market?'
res = chain.invoke({'question': question})
print(res)