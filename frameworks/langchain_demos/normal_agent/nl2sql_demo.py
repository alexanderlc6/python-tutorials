
messages=[]
messages.append({'role': 'system', 'content': 'Answer user questions by generating SQL queries against the Chinook Music Database.'})
messages.append({'role': 'user', 'content': 'Hi, who are the top 5 artists by number of tracks?'})

chat_response = chat_completion_request(messages, functions)
assistant_msg = chat_response.json()['choices'][0]['message']
messages.append(assistant_msg)

if assistant_msg.get('functional_call'):
    results = execute_function_call(assistant_msg)
    messages.append({'role': 'function', 'name': assistant_msg['function_call']['name'], 'content': results})

pretty_print_conversation(messages)