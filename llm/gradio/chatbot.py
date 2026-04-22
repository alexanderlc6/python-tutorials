import gradio as gr
import random
import time

from click import style


def bot(history):
    # bot_message = random.choice(["你好吗？", "我爱你", "我很饿"])
    # history[-1][1] = ''
    # for character in bot_message:
    #     history[-1][1] += character
    #     time.sleep(0.05)
    #     yield history
    response = "**That's cool!**"
    history[-1][1] = response
    return history


def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id='chatbot')  #.style(color_map=("green", "pink"))
    # msg = gr.Textbox()
    # clear = gr.Button("清除")

    # Sync mode
    # def respond(message, chat_history):
    #     bot_message = random.choice(["你好吗？", "我爱你", "我很饿"])
    #     chat_history.append((message, bot_message))
    #     time.sleep(1)
    #     return "", chat_history
    #
    # msg.submit(respond, [msg, chatbot], [msg, chatbot])
    # clear.click(lambda: None, None, chatbot, queue=False)

    # Async mode
    #     def user(user_message, history):
    #         return "", history + [[user_message, None]]
    #
    #     msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
    #         bot, chatbot, chatbot
    #     )
    #     clear.click(lambda: None, None, chatbot, queue=False)
    # demo.queue()

    with gr.Row():
        with gr.Column(scale=0.85):
            txt = gr.Textbox(
                show_label=False,
                placeholder='Input text to summit or upload image'
            )
            txt.container = False
        with gr.Column(scale=0.15, min_width=0):
            btn = gr.UploadButton("上传图片", file_types=['image', 'video', 'audio'])

    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )
    btn.upload(add_file, [chatbot, btn], [chatbot]).then(
        bot, chatbot, chatbot
    )


demo.launch()