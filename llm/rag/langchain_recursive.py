# langchain==0.2.1
from langchain.text_splitter import RecursiveCharacterTextSplitter

text = '自然语言处理( Natural Language Processing, NLP)是人工智能领域的重要研究方向, 融合了语言学、计算机科学、机器学习、数学、认知心理学等多个学科领域的知识。它是一门集计算机科学、人工智能和语言学于一体的交叉学科。它包含自然语言理解和自然语言生成两个主要方面, 研究内容包括字、词、短语、句子、段落和篇章等多种层次。它是机器语言和人类语言之间沟通的桥梁。它旨在使机器理解、解释并生成人类语言，实现人机之间有效沟通，使计算机能够执行语言翻译、情感分析、文本摘要等任务。'

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 50,
    chunk_overlap = 10,
    length_function = len
)

chunks = splitter.split_text(text)

for i, chunk in enumerate(chunks):
    print(f'Block {i + 1}:{len(chunk)}:{chunk}')