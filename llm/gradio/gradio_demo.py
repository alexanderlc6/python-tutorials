import gradio as gr
import numpy as np
import cv2
import time

from langchain_community.chat_models import ChatOpenAI


def reverse_text_count(text):
    reverse_text = text[::-1]
    length = len(text)
    return reverse_text, length

def say(name):
    return 'Hello' + name

def img_to_sketch(image):
    gray_image = image.convert('L')
    inverted_img = 255 - np.array(gray_image)
    blurred = cv2.GaussianBlur(inverted_img, (21, 21), 0)
    inverted_blurred = 255 - blurred
    pencil_sketch = cv2.divide(np.array(gray_image), inverted_blurred, scale=256.0)
    return pencil_sketch

# demo = gr.Interface(fn = reverse_text_count, inputs = 'text', outputs = ['text','number'],
#                     title='Text output tool', description='Text Tool')


def demo_fn(text, num, slider_val, check1, check2, dropdown_choice, image, audio, video):
    # 文本输出
    text_out = f"文本输入: {text}"

    # 数字输出
    number_out = f"数字输入: {num}, 加10 = {num + 10}"

    # 滑块输出
    slider_out = f"滑块值: {slider_val}, 平方 = {slider_val ** 2}"

    # 复选框输出
    checks = []
    if check1: checks.append("Option 1")
    if check2: checks.append("Option 2")
    checkbox_out = "选择了: " + (", ".join(checks) if checks else "无")

    # 下拉输出
    dropdown_out = f"下拉选择: {dropdown_choice}"

    # 图片输出: 原图 + 反色图
    if image is not None:
        inverted_image = Image.fromarray(255 - np.array(image))
    else:
        inverted_image = None

    # 音频输出: 原样返回
    audio_out = audio

    # 视频输出: 原样返回
    video_out = video

    # 返回多个输出
    return text_out, number_out, slider_out, checkbox_out, dropdown_out, image, inverted_image, audio_out, video_out


demo = gr.Interface(fn = img_to_sketch, inputs = [gr.Image(label='UploadImage', type='pil')],
                    outputs=[gr.Image(label='SketchImage')],
                    title='Image to pencil picture', description='Image to pencil picture')

iface = gr.Interface(
    fn=demo_fn,
    inputs=[
        gr.Textbox(label="文本输入"),
        gr.Number(label="数字输入"),
        gr.Slider(0, 100, label="滑块"),
        gr.Checkbox(label="Option 1"),
        gr.Checkbox(label="Option 2"),
        gr.Dropdown(choices=["A", "B", "C"], label="下拉菜单"),
        gr.Image(label="上传图片"),
        gr.Audio(sources=["upload"], type="numpy", label="上传音频"),
        gr.Video(label="上传视频")
    ],
    outputs=[
        gr.Textbox(label="文本输出"),
        gr.Textbox(label="数字输出"),
        gr.Textbox(label="滑块输出"),
        gr.Textbox(label="复选框输出"),
        gr.Textbox(label="下拉输出"),
        gr.Image(label="原图"),
        gr.Image(label="反色图"),
        gr.Audio(label="音频输出"),
        gr.Video(label="视频输出")
    ],
    title="Interface 示例",
    description="Gradio输入输出示例"
)

def calculate_bmi(height, weight):
    bmi = weight / (height/100)**2
    return bmi, "正常" if 18.5 <= bmi <= 24 else "不正常"

demo = gr.Interface(
    fn=calculate_bmi,
    inputs=[gr.Number(label="身高(cm)"), gr.Number(label="体重(kg)")],
    outputs=[gr.Number(label="BMI"), gr.Textbox(label="状态")],
)

# Tabs
with gr.Blocks() as demo:
    with gr.Tab("翻译"):
        # 翻译界面内容
        pass
    with gr.Tab("语音识别"):
        # 语音识别内容
        pass

# Event process
def update(name):
    return f"Welcome, {name}!"

with gr.Blocks() as demo:
    name = gr.Textbox(label="Name")
    output = gr.Textbox(label="Output")
    name.change(fn=update, inputs=name, outputs=output)

# Progress bar
def slow_fn():
    for i in gr.Progress(range(100)):
        time.sleep(0.1)
    return "Done!"

# gr.Interface(
#     examples=[["John"], ["Alice"]],  # 为每个输入提供示例
#     examples_per_page=10
# )

# def process_images(images):
#     return [process(img) for img in images]
#
# gr.Interface(fn=process_images, inputs=gr.Gallery(), outputs=gr.Gallery())

# Load cached model
# @gr.cache()
# def load_model():
#     return torch.load('large_model.pth')

# def batch_predict(images):
#     return model.predict(np.stack(images))


# import torch
# model = torch.load('model.pth')

# Integrate with PyTorch/TensorFlow
# def predict(image):
#     image = preprocess(image)
#     prediction = model(image)
#     return postprocess(prediction)
# gr.Interface(fn=predict, inputs="image", outputs="label").launch()

# Integrate with HuggingFace
from transformers import pipeline
import os
classifier = pipeline(model='Qwen/Qwen3.5-397B-A17B', token=os.getenv('HF_TOKEN'), task="text-classification")
gr.Interface(
    fn=classifier,
    inputs=gr.Textbox(placeholder='Please input text to be classified'),
    outputs=gr.Label(num_top_classes=3)
)

# Set max concurrent task count
# demo.queue(concurrent_count=3)
demo.launch(share=True, css=".gradio-container {background-color: red}")

