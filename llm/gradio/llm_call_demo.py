import os
from openai import OpenAI

# Get Qwen Dashscope api key from env var
api_key = os.getenv('DASHSCOPE_API_KEY')
print(api_key)

# if not api_key: ...

def call_qwen(message, history):
    if not api_key:
        return 'Error: not configured DASHSCOPE_API_KEY env var, please retry after configuration.'

    client = OpenAI(api_key = api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

    messages = []

    # Process Gradio ChatInterface message format
    if history:
        try:
            for msg in history:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append(msg)
                elif isinstance(msg, (list, tuple)) and len(msg) == 2:
                    user_msg, assistant_msg = msg
                    messages.append({'role': 'user', 'content':user_msg})
                    messages.append({'role': 'assistant', 'content':assistant_msg})
        except Exception as e:
            print(f'Error occurred when process history record: {e}')

    messages.append({'role': 'user', 'content':message})

    try:
        response = client.chat.completions.create(
            model = 'qwen-max',
            messages=messages,
            stream=False
        )

        return response.choices[0].message.content
    except Exception as e:
        return 'Error:' + str(e)

# Use ChatInterface component
import gradio as gr
demo = gr.ChatInterface(
    fn = call_qwen,
    title='Qwen-max',
    description='Qwen chat robot',
    examples=[
        ['Hello'],
        ['What is your name?'],
        ['What is your favorite color?'],
        ['What is your favorite food?']
    ]
)

if __name__ == '__main__':
    demo.launch(theme=gr.themes.Soft())