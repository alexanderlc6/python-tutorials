import json
import re
from collections import Counter

import numpy as np
from langchain_community.utils.math import cosine_similarity

with open('ques1.json','r', encoding='utf-8') as f:
    papers = json.load(f)

print('Raw data preview:', json.dumps(papers, ensure_ascii=False, indent=2))

class MedicalLiteratureProcessor:
    def __init__(self):
        # 定义医学停用词（常见但无意义的词汇）
        self.stop_words = {
            '的', '了', '和', '是', '在', '有', '被', '与', '及', '等', '对', '为', '之',
            '本文', '研究', '分析', '探讨', '总结', '表明', '显示', '方法', '包括',
            '需要', '主要', '重要', '之一', '患者', '疾病', '因素', '标准', '效果',
            '治疗', '进行', '通过', '以及', '其', '该', '上述', '这些', '那些',
            '我们', '他们', '它们', '它', '他', '她', '你', '我',
            '一个', '一种', '一些', '部分', '方面', '过程', '结果', '目的',
            '可以', '可能', '应该', '必须', '能够', '已经', '正在', '将会',
            '由于', '因为', '所以', '因此', '但是', '然而', '虽然', '如果',
            '例如', '比如', '如图', '如下', '所示', '所述', '所述的', '对比',
            '介绍', '威胁', '人类', '健康', '对比了', '总结了', '探讨了',
            '本文介绍', '本文总结', '本研究', '分析了', '讨论了'
        }

        # 医学术语词典（按长度降序，优先匹配长词）
        self.medical_terms = [
            # 疾病名称
            '糖尿病', '高血压', '心脏病', '心血管疾病', '冠心病', '心肌梗塞',
            '脑卒中', '动脉硬化', '心力衰竭', '心律失常', '高血脂', '高血糖',
            # 治疗方法
            '胰岛素治疗', '口服药物', '药物治疗', '饮食控制', '运动锻炼',
            '定期体检', '综合治疗', '手术治疗', '介入治疗', '药物治疗方案',
            # 诊断评估
            '临床诊断', '诊断标准', '风险因素', '危险因素', '病因分析',
            '病理生理', '发病机制', '预后评估', '随访观察',
            # 其他医学术语
            '血压控制', '血糖控制', '血脂管理', '体重管理', '生活方式',
            '并发症', '合并症', '发病率', '患病率', '死亡率', '生存率',
            '临床试验', '随机对照', '双盲试验', '安慰剂', '疗效评估', '副作用',
            '生化指标', '体格检查', '影像学检查', '实验室检查'
        ]
        self.medical_terms.sort(key=len, reverse=True)

    def clean_html(self, text):
        """数据清洗,清除HTML标签"""
        if not text:
            return ''

        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 去除HTML实体（如 &nbsp;, &lt; 等）
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        text = re.sub(r'&#[0-9]+;', ' ', text)
        # 去除特殊字符，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\\s,。;:！？、""''（）]', ' ', text)
        # 合并多个空格
        text = re.sub(r'\\s+', ' ', text)
        return text.strip()

    def extract_keywords(self, text, top_k = 5):
            """
            关键词提取：基于词频统计和医学术语识别
            使用简单的分词策略：
            1. 优先识别医学术语词典中的复合词
            2. 然后按字符进行n-gram提取（2-4字词）
            3. 过滤停用词和单字词
            """
            if not text:
                return []

            keywords = []

            # 步骤1：识别医学术语词典中的词
            remaining_text = text
            for term in self.medical_terms:
                if term in remaining_text:
                    count = remaining_text.count(term)
                    keywords.extend([term] * count)

                    # 从文本中移除已识别的术语，避免重复计数
                    remaining_text = remaining_text.replace(term, ' ')

            # 步骤2：n-gram分词（2-4字）
            def get_ngrams(s, n):
                """获取n-gram"""
                return [s[i:i+n] for i in range((len(s) - n + 1))]

            # 清理后的文本进行n-gram提取
            # 只保留中文字符进行分词
            chinese_text = re.sub(r'[^\u4e00-\u9fa5]', '', remaining_text)
            ngram_words = []

            # 从4字到2字
            for n in range(4, 1, -1):
                ngrams = get_ngrams(chinese_text, n)
                for gram in ngrams:
                    # 过滤条件：不含停用词、不是纯数字、长度合适
                    if gram not in self.stop_words \
                        and not re.match(r'^\\d+$', gram) and len(gram) >= 2:
                        ngram_words.append(gram)

            # 步骤3：合并所有关键词并统计词频
            all_keywords = ngram_words + keywords
            word_counts = Counter(all_keywords)

            # 步骤4：过滤和排序--过滤低频词和进一步清洗
            # 只保留出现次数>=1的词，并按频率排序
            filtered_words = []
            for word, count in word_counts.items():
                if word in self.stop_words:
                    continue
                # 过滤包含过多停用词字符的词
                stop_char_ratio = sum(1 for c in word if c in '的了和是在有') / len(word)
                if stop_char_ratio > 0.5:
                    continue
                filtered_words.append((word, count))

            # 排序策略：医学术语优先，然后按词频。
            def sort_key(item):
                word, count = item
                # 是否在医学词典中
                is_medical_item = word in self.medical_terms
                if is_medical_item:
                    # 医学术语+1000分
                    priority = 1000
                else:
                    priority = 0
                # 先按加权频次，再按词长
                return (priority + count, len(word))
            # 示例排序结果:
            # ("糖尿病", 2)    → (1002, 3)  # 医学术语+高频，排第一
            # ("治疗", 5)      → (5, 2)     # 非术语，排后面
            # ("胰岛素治疗", 1) → (1001, 4) # 医学术语，排第二

            filtered_words.sort(key=sort_key, reverse=True)
            return [word for word, count in filtered_words[:top_k]]
            # filtered_counter = Counter({word: word_counts[word] for word in filtered_counts})
            # # 返回top_k关键词
            # top_keywords = filtered_counts.most_common(top_k)
            # return [word for word, count in top_keywords]

    def process_papers(self, papers):
        """
        处理整个文献数据集
        """
        processed_data = []
        for paper in papers:
            # 1. 数据清洗
            clean_title = self.clean_html(paper.get('title', ''))
            clean_abstract = self.clean_html(paper.get('abstract', ''))

            # 2. 关键词提取（从标题和摘要中提取）
            combined_text = clean_title + ' ' + clean_abstract
            keywords = self.extract_keywords(combined_text, top_k=5)

            # 3. 构建处理后的数据
            processed_paper = {
                'id': paper.get('id'),
                'title': clean_title,
                'abstract': clean_abstract,
                'publish_date': paper.get('publish_date'),
                'keywords': keywords,
                'text_for_vectorization': f'{clean_title}。{clean_abstract} Keywords: {', '.join(keywords)}'
            }

            processed_data.append(processed_paper)
            return processed_data

    def get_vectorization_format(self, processed_data):
        """
        转换为适合向量化的格式
        返回结构化数据，便于后续向量化处理
        """
        vectorization_data = []

        for paper in processed_data:
            vectorization_data.append({
                'doc_id': paper['id'],
                'content': paper['text_for_vectorization'],
                'metadata': {
                    'title': paper['title'],
                    'publish_date': paper['publish_date'],
                    'keywords': paper['keywords']
                }
            })
            return vectorization_data


# ==================== 向量化引擎 ====================
class VectorizationEngine:
    """向量化引擎 - 支持本地模型和API"""

    def __init__(self, model_type='local', api_key=None):
        self.model_type = model_type
        self.model = None
        self.api_key = api_key

        if model_type == 'local':
            self._init_local_model()

    def _init_local_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            print("🔄 正在加载本地模型: shibing624/text2vec-base-chinese...")
            self.model = SentenceTransformer('shibing624/text2vec-base-chinese')
            print('Model loaded...')
        except ImportError:
            print("⚠️ 缺少依赖库：sentence_transformers, 使用模拟向量演示")
            self.model = None

    def vectorize(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        if self.model_type == 'local' and self.model is not None:
            return self._vectorize_local(texts)
        else:
            return self.vectorize_api(texts)

    def _vectorize_local(self, texts):
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    def _vectorize_mock(self, texts):
        """模拟向量化结果"""
        print('使用模拟向量(随机生成)')
        # 生成768维的模拟向量（与text2vec-base-chinese维度一致）
        import numpy as np
        np.random.seed(42)
        return np.random.rand(len(texts), 768).astype(np.float32)

    def vectorize_api(self, texts):
        """API向量化示例（OpenAI/智谱）"""
        from zhipuai import ZhipuAI
        client = ZhipuAI(api_key=self.api_key)
        response = client.embeddings.create(model='embedding-2', input=texts)
        return np.array([item.embedding for item in response.data])

        # from openai import OpenAI
        # import os
        # client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.chatanywhere.tech")
        # data = client.embeddings.create(input=texts, model='text-embedding-3-large').data
        # return np.array([x.embedding for x in data])

    def similarity_search(self, query, corpus_embeddings, corpus_data, top_k=3):
        query_embedding = self.vectorize([query])
        similarities = cosine_similarity(query_embedding, corpus_embeddings)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                'rank': len(results) + 1,
                'doc_id': corpus_data[idx]['doc_id'],
                'title': corpus_data[idx]['metadata']['title'],
                'similarity': float(similarities[idx]),
                'keywords': corpus_data[idx]['metadata']['keywords']
            })

        return results

    # ==================== 运行完整流程 ====================
    print("=" * 70)
    print("🔬 医学文献处理 + 向量化系统")
    print("=" * 70)

if __name__ == "__main__":
    # 初始化处理器
    # 步骤1: 数据预处理
    print("\n【步骤1】数据清洗与关键词提取...")
    processor = MedicalLiteratureProcessor()

    # 处理数据
    processed_papers = processor.process_papers(papers)
    # print("=" * 60)
    # print('Processed Cleaning data:')
    # print("=" * 60)
    # for paper in processed_papers:
    #     print(f"\n文献ID: {paper['id']}")
    #     print(f"Cleaned Title: {paper['title']}")
    #     print(f"Cleaned Abstract: {paper['abstract']}")
    #     print(f"Publish Date: {paper['publish_date']}")
    #     print(f"Text for Vectorization: {paper['text_for_vectorization']}")
    #     print("-" * 60)
    #
    # print("=" * 60)
    # print('Keyword fetch result based on frequency statistics:')
    # print("=" * 60)
    # for paper in processed_papers:
    #     print(f"\n文献ID: {paper['id']}-{paper['title']}")
    #     print(f"Fetched Keywords: {paper['keywords']}")
    #     print(f"Keyword count: {len(paper['keywords'])}")
    #     print("-" * 60)

    # 展示处理流程总结
    print("=" * 70)
    print("📊 医学文献处理系统 - 处理流程总结")
    print("=" * 70)

    print("\n【输入数据】")
    print(f"文献数量: {len(papers)}")
    for p in papers:
        print(f"  - {p['id']}: {p['title']}")

    print("\n【处理结果】")
    for paper in processed_papers:
        print(f"\n📄 文献 {paper['id']}: {paper['title']}")
        print(f"   发布日期: {paper['publish_date']}")
        print(f"   关键词: {', '.join(paper['keywords'])}")
        print(f"   向量化文本长度: {len(paper['text_for_vectorization'])} 字符")

    print("\n" + "=" * 70)
    print("✅ 处理完成！数据已准备好进行向量化,处理文献数: {len(vectorization_data)}")
    print("=" * 70)
    # print("\n向量化建议：")
    # print("1. 使用预训练的中文医学BERT模型（如 mc-bert, PCL-MedBERT）")
    # print("2. 或使用通用中文Embedding模型（如 text2vec, GanymedeNil/text2vec-large-chinese）")
    # print("3. 关键词可用于构建稀疏向量，与稠密向量结合进行混合检索")

    # 获取向量化格式数据
    vectorization_data = processor.get_vectorization_format(processed_papers)
    print("=" * 70)
    print('Vectorization format data:')
    print(json.dumps(vectorization_data, ensure_ascii=False, indent=2))

    for item in vectorization_data:
        print(f'Doc:{item["doc_id"]}:{item['metadata']['title']}')
        print(f'Keywords:{', '.join(item["metadata"]['keywords'])}')

    print("\n【步骤2】文本向量化...")
    vector_engine = VectorizationEngine(model_type='local')
    corpus_texts = [item['content'] for item in vectorization_data]
    corpus_embeddings = vector_engine.vectorize(corpus_texts)

    print(f"✅ 向量化完成！")
    print(f"   向量矩阵形状: {corpus_embeddings.shape}")
    print(f"   向量维度: {corpus_embeddings.shape[1]} 维")
    print(f"   数据类型: {corpus_embeddings.dtype}")

    # 步骤3: 向量存储与展示
    print("\n【步骤3】向量存储结构：")
    for i, item in enumerate(vectorization_data):
        emb = corpus_embeddings[i]
        print(f"\n Doc: {item['doc_id']}:{item['metadata']['title']}")
        print(f'Vector shape: {emb.shape}')
        print(f'First 5 dims:[{', '.join([f'{x:.4f}' for x in emb[:5]])}]')
        print(f'L2: {np.linalg.norm(emb):.4f}')
        print(f'Store size: {emb.nbytes} bytes({emb.nbytes / 1024:.2f} KB')

    # 步骤4: 相似度检索演示
    print("\n" + "=" * 70)
    print("🔍 相似度检索演示")
    print("=" * 70)

    # 测试查询
    queries = [
        "胰岛素治疗糖尿病的方法",
        "心血管疾病的预防措施",
        "高血压的诊断标准是什么"
    ]

    for query in queries:
        print(f"\n查询: \"{query}\"")
        results = vector_engine.similarity_search(query, corpus_embeddings, vectorization_data, top_k=2)
        for res in results:
            print(f" Rank:{res['rank']}: [{res['doc_id']}] {res['title']}")
            print(f"           相似度: {res['similarity']:.4f}")
            print(f"           关键词: {', '.join(res['keywords'])}")

print("\n" + "=" * 70)
print("✅ 完整流程演示结束！")
print("=" * 70)
