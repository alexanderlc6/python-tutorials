from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

class Movie(BaseModel):
    title: str = Field(..., description="The title of the movie")
    director: str = Field(..., description="The director of the movie")
    year: int = Field(..., description="The year the movie was released")
    rating: float = Field(..., description="The rating of the movie")

model_with_structure = model.with_structured_output(Movie, method='function_calling',
                                                    include_raw=True)
# Qwen require prompt includes keyword [JSON format]
response = model_with_structure.invoke('Provide details about the movie Inception in JSON format'
                                       'with title,director, year, rating')
print('Raw:', response['raw'])
print('Parsed:', response['parsed'])