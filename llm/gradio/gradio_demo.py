import gradio as gr
import numpy as np
import cv2

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

demo = gr.Interface(fn = img_to_sketch, inputs = [gr.Image(label='UploadImage', type='pil')],
                    outputs=[gr.Image(label='SketchImage')],
                    title='Image to pencil picture', description='Image to pencil picture')
demo.launch()

