from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os, json

from basic.validator.msg_validator import ValidationError

model = ChatOpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),model='qwen-max',
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

class Movie(BaseModel):
    title: str = Field(..., description="The title of the movie")
    director: str = Field(default='', description="The director of the movie")
    year: int = Field(default=0, description="The year the movie was released")
    rating: float = Field(default=0.0, description="The rating of the movie")

class Actor(BaseModel):
    name: str
    rule: str

class MovieDetails(BaseModel):
    title: str
    year: int
    cast: list[Actor]
    genres: list[str]
    budget: float | None = Field(None, description="The budget of the movie")

# Method 1:
# Specify to use [function_calling] method(default is json_mode) and return raw content
# model_info_with_structure = model.with_structured_output(Movie, method='function_calling',
#                                                     include_raw=True)
# Qwen require prompt includes keyword [JSON format]
# response = model_with_structure.invoke('Provide details about the movie Inception in JSON format'
#                                        'with title,director, year, rating')
# print('Raw:', response['raw'])
# print('Parsed:', response['parsed'])
# Output:
# Raw: content='' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 36, 'prompt_tokens': 251, 'total_tokens': 287, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-max', 'system_fingerprint': None, 'id': 'chatcmpl-b457f906-ca82-9d9c-b00f-7e8e9e1f5af3', 'finish_reason': 'tool_calls', 'logprobs': None} id='lc_run--019ce56e-4c17-7ae2-9583-fb690920a8cf-0' tool_calls=[{'name': 'Movie', 'args': {'title': 'Inception', 'director': 'Christopher Nolan', 'year': 2010, 'rating': 8.8}, 'id': 'call_136a2c2a4b084b0bb56106', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 251, 'output_tokens': 36, 'total_tokens': 287, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}
# Parsed: title='Inception' director='Christopher Nolan' year=2010 rating=8.8

model_details_with_structure = model.with_structured_output(MovieDetails, method='json_schema',
                                                             include_raw=True)
query_details_response = model_details_with_structure.invoke('Provide details about the movie Inception in JSON format')

# Output with method='function_calling'
# Actual data in raw.tool_calls(raw.content is empty since we use [function_calling] method)
# raw = query_details_response['raw']
# print('Raw:', raw)
# if hasattr(raw, 'tool_calls'):
#     print('Tool Calls:', raw.tool_calls)
# elif 'tool_calls' in raw.additional_kwargs:
#     print('Tool Calls:', raw.additional_kwargs['tool_calls'])
# parsed = query_details_response['parsed']
# print("Parsed:", parsed)
# print("Title:", parsed.title)
# print("Cast:", parsed.cast)
print(query_details_response)
# Output:
# Raw: content='' additional_kwargs={'refusal': None} response_metadata={'token_usage': {'completion_tokens': 101, 'prompt_tokens': 285, 'total_tokens': 386, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-max', 'system_fingerprint': None, 'id': 'chatcmpl-774461d7-4321-9c23-93a9-0e2d9b1935cc', 'finish_reason': 'tool_calls', 'logprobs': None} id='lc_run--019ce61f-30b0-7022-a716-de30308fcb94-0' tool_calls=[{'name': 'MovieDetails', 'args': {'title': 'Inception', 'year': 2010, 'cast': [{'name': 'Leonardo DiCaprio', 'rule': 'Cobb'}, {'name': 'Joseph Gordon-Levitt', 'rule': 'Arthur'}, {'name': 'Ellen Page', 'rule': 'Ariadne'}], 'genres': ['Action', 'Adventure', 'Sci-Fi'], 'budget': 160000000}, 'id': 'call_72316dc6070747deb6d560', 'type': 'tool_call'}] invalid_tool_calls=[] usage_metadata={'input_tokens': 285, 'output_tokens': 101, 'total_tokens': 386, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}
# # Parsed: title='Inception' year=2010 cast=[Actor(name='Leonardo DiCaprio', rule='Cobb'), Actor(name='Joseph Gordon-Levitt', rule='Arthur'), Actor(name='Ellen Page', rule='Ariadne')] genres=['Action', 'Adventure', 'Sci-Fi'] budget=160000000.0
# # {'raw': AIMessage(content='', additional_kwargs={'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 101, 'prompt_tokens': 285, 'total_tokens': 386, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-max', 'system_fingerprint': None, 'id': 'chatcmpl-774461d7-4321-9c23-93a9-0e2d9b1935cc', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--019ce61f-30b0-7022-a716-de30308fcb94-0', tool_calls=[{'name': 'MovieDetails', 'args': {'title': 'Inception', 'year': 2010, 'cast': [{'name': 'Leonardo DiCaprio', 'rule': 'Cobb'}, {'name': 'Joseph Gordon-Levitt', 'rule': 'Arthur'}, {'name': 'Ellen Page', 'rule': 'Ariadne'}], 'genres': ['Action', 'Adventure', 'Sci-Fi'], 'budget': 160000000}, 'id': 'call_72316dc6070747deb6d560', 'type': 'tool_call'}], invalid_tool_calls=[], usage_metadata={'input_tokens': 285, 'output_tokens': 101, 'total_tokens': 386, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}), 'parsed': MovieDetails(title='Inception', year=2010, cast=[Actor(name='Leonardo DiCaprio', rule='Cobb'), Actor(name='Joseph Gordon-Levitt', rule='Arthur'), Actor(name='Ellen Page', rule='Ariadne')], genres=['Action', 'Adventure', 'Sci-Fi'], budget=160000000.0), 'parsing_error': None}

# Output with method='json_mode'
# {'raw': AIMessage(content='{\n  "title": "Inception",\n  "year": 2010,\n  "director": "Christopher Nolan",\n  "writers": ["Christopher Nolan"],\n  "cast": [\n    {\n      "actor": "Leonardo DiCaprio",\n      "character": "Cobb"\n    },\n    {\n      "actor": "Joseph Gordon-Levitt",\n      "character": "Arthur"\n    },\n    {\n      "actor": "Ellen Page",\n      "character": "Ariadne"\n    },\n    {\n      "actor": "Tom Hardy",\n      "character": "Eames"\n    },\n    {\n      "actor": "Ken Watanabe",\n      "character": "Saito"\n    },\n    {\n      "actor": "Dileep Rao",\n      "character": "Yusuf"\n    },\n    {\n      "actor": "Cillian Murphy",\n      "character": "Robert Fischer"\n    },\n    {\n      "actor": "Tom Berenger",\n      "character": "Peter Browning"\n    },\n    {\n      "actor": "Marion Cotillard",\n      "character": "Mal"\n    }\n  ],\n  "genre": ["Action", "Adventure", "Sci-Fi"],\n  "runtime": "148 minutes",\n  "production_company": "Legendary Pictures, Syncopy",\n  "distributor": "Warner Bros. Pictures",\n  "plot_summary": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO\'s son.",\n  "awards": [\n    "Academy Award for Best Cinematography",\n    "Academy Award for Best Sound Editing",\n    "Academy Award for Best Sound Mixing",\n    "Academy Award for Best Visual Effects"\n  ]\n}', additional_kwargs={'parsed': None, 'refusal': None}, response_metadata={'token_usage': {'completion_tokens': 378, 'prompt_tokens': 20, 'total_tokens': 398, 'completion_tokens_details': None, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'qwen-max', 'system_fingerprint': None, 'id': 'chatcmpl-64adb458-b546-91fb-9470-896738c3de50', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--019ce62e-6a40-7560-9cf9-77aaffd82934-0', tool_calls=[], invalid_tool_calls=[], usage_metadata={'input_tokens': 20, 'output_tokens': 378, 'total_tokens': 398, 'input_token_details': {'cache_read': 0}, 'output_token_details': {}}), 'parsing_error': OutputParserException('Failed to parse MovieDetails from completion {"title": "Inception", "year": 2010, "director": "Christopher Nolan", "writers": ["Christopher Nolan"], "cast": [{"actor": "Leonardo DiCaprio", "character": "Cobb"}, {"actor": "Joseph Gordon-Levitt", "character": "Arthur"}, {"actor": "Ellen Page", "character": "Ariadne"}, {"actor": "Tom Hardy", "character": "Eames"}, {"actor": "Ken Watanabe", "character": "Saito"}, {"actor": "Dileep Rao", "character": "Yusuf"}, {"actor": "Cillian Murphy", "character": "Robert Fischer"}, {"actor": "Tom Berenger", "character": "Peter Browning"}, {"actor": "Marion Cotillard", "character": "Mal"}], "genre": ["Action", "Adventure", "Sci-Fi"], "runtime": "148 minutes", "production_company": "Legendary Pictures, Syncopy", "distributor": "Warner Bros. Pictures", "plot_summary": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO\'s son.", "awards": ["Academy Award for Best Cinematography", "Academy Award for Best Sound Editing", "Academy Award for Best Sound Mixing", "Academy Award for Best Visual Effects"]}. Got: 19 validation errors for MovieDetails\ncast.0.name\n  Field required [type=missing, input_value={\'actor\': \'Leonardo DiCap...o\', \'character\': \'Cobb\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.0.rule\n  Field required [type=missing, input_value={\'actor\': \'Leonardo DiCap...o\', \'character\': \'Cobb\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.1.name\n  Field required [type=missing, input_value={\'actor\': \'Joseph Gordon-..., \'character\': \'Arthur\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.1.rule\n  Field required [type=missing, input_value={\'actor\': \'Joseph Gordon-..., \'character\': \'Arthur\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.2.name\n  Field required [type=missing, input_value={\'actor\': \'Ellen Page\', \'character\': \'Ariadne\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.2.rule\n  Field required [type=missing, input_value={\'actor\': \'Ellen Page\', \'character\': \'Ariadne\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.3.name\n  Field required [type=missing, input_value={\'actor\': \'Tom Hardy\', \'character\': \'Eames\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.3.rule\n  Field required [type=missing, input_value={\'actor\': \'Tom Hardy\', \'character\': \'Eames\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.4.name\n  Field required [type=missing, input_value={\'actor\': \'Ken Watanabe\', \'character\': \'Saito\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.4.rule\n  Field required [type=missing, input_value={\'actor\': \'Ken Watanabe\', \'character\': \'Saito\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.5.name\n  Field required [type=missing, input_value={\'actor\': \'Dileep Rao\', \'character\': \'Yusuf\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.5.rule\n  Field required [type=missing, input_value={\'actor\': \'Dileep Rao\', \'character\': \'Yusuf\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.6.name\n  Field required [type=missing, input_value={\'actor\': \'Cillian Murphy...cter\': \'Robert Fischer\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.6.rule\n  Field required [type=missing, input_value={\'actor\': \'Cillian Murphy...cter\': \'Robert Fischer\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.7.name\n  Field required [type=missing, input_value={\'actor\': \'Tom Berenger\',...cter\': \'Peter Browning\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.7.rule\n  Field required [type=missing, input_value={\'actor\': \'Tom Berenger\',...cter\': \'Peter Browning\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.8.name\n  Field required [type=missing, input_value={\'actor\': \'Marion Cotillard\', \'character\': \'Mal\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ncast.8.rule\n  Field required [type=missing, input_value={\'actor\': \'Marion Cotillard\', \'character\': \'Mal\'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\ngenres\n  Field required [type=missing, input_value={\'title\': \'Inception\', \'y...r Best Visual Effects\']}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\nFor troubleshooting, visit: https://docs.langchain.com/oss/python/langchain/errors/OUTPUT_PARSING_FAILURE '), 'parsed': None}


# Method 2: Define prompt text
# prompt = '''You must response with a valid JSON object containing exactly these fields:
# - title (string)
# - director (string)
# - year (integer)
# - rating (float between 0-10)
#
# Example: {{"title":"The matrix", "director": "Wachowski Sisters", "year": 2001, "rating": 8.5}}
# Now provide details about the movie Inception
# '''
#
# response = model.invoke(prompt)
#
# # Manually resolve response result
# try:
#     content = response.content
#     if "```json" in content:
#         content = content.split("```json")[1].split("```")[0]
#     elif "```" in content:
#         content = content.split("```")[1].split("```")[0]
#
#     data = json.loads(content.strip())
#     movie = Movie(**data)
#     print(movie)
# except (json.JSONDecodeError, ValidationError) as e:
#     print(f'Parse error: {e}')
#     print(f'Raw content: {response.content}')

