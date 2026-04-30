# 完整代码整合：医学文献处理 + 向量化系统

import json
import re
import numpy as np
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity


# ==================== 1. 文献处理器 ====================

class MedicalLiteratureProcessor:
    """医学文献处理系统"""

    def __init__(self):
        self.stop_words = {'的', '了', '和', '是', '在', '有', '被', '与', '及', '等', '对', '为', '之',
                           '本文', '研究', '分析', '探讨', '总结', '表明', '显示', '方法', '包括',
                           '需要', '主要', '重要', '之一', '患者', '疾病', '因素', '标准', '效果',
                           '治疗', '进行', '通过', '以及', '其', '该', '上述', '这些', '那些',
                           '我们', '他们', '它们', '它', '他', '她', '你', '我',
                           '一个', '一种', '一些', '部分', '方面', '过程', '结果', '目的',
                           '可以', '可能', '应该', '必须', '能够', '已经', '正在', '将会',
                           '由于', '因为', '所以', '因此', '但是', '然而', '虽然', '如果',
                           '例如', '比如', '如图', '如下', '所示', '所述', '所述的', '对比',
                           '介绍', '威胁', '人类', '健康', '对比了', '总结了', '探讨了'}

        self.medical_terms = ['糖尿病', '高血压', '心脏病', '心血管疾病', '胰岛素治疗', '口服药物',
                              '饮食控制', '运动锻炼', '定期体检', '综合治疗', '临床诊断', '诊断标准',
                              '风险因素', '危险因素', '病因分析', '预防']
        self.medical_terms.sort(key=len, reverse=True)

    def clean_html(self, text):
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        text = re.sub(r'&#[0-9]+;', ' ', text)
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s，。；：！？、""''（）]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_keywords(self, text, top_k=5):
        if not text:
            return []

        keywords = []
        remaining_text = text

        # 医学术语词典匹配
        for term in self.medical_terms:
            if term in remaining_text:
                count = remaining_text.count(term)
                keywords.extend([term] * count)
                remaining_text = remaining_text.replace(term, ' ')

        # n-gram分词
        def get_ngrams(s, n):
            return [s[i:i + n] for i in range(len(s) - n + 1)]

        chinese_text = re.sub(r'[^\u4e00-\u9fa5]', '', remaining_text)
        ngram_words = []
        for n in range(4, 1, -1):
            ngrams = get_ngrams(chinese_text, n)
            for gram in ngrams:
                if (gram not in self.stop_words and
                        not re.match(r'^\d+$', gram) and len(gram) >= 2):
                    ngram_words.append(gram)

        all_keywords = keywords + ngram_words
        word_counts = Counter(all_keywords)

        filtered_words = []
        for word, count in word_counts.items():
            if word in self.stop_words:
                continue
            stop_char_ratio = sum(1 for c in word if c in '的了和是在有与及之') / len(word)
            if stop_char_ratio > 0.5:
                continue
            filtered_words.append((word, count))

        def sort_key(item):
            word, count = item
            is_medical_term = word in self.medical_terms
            priority = 1000 if is_medical_term else 0
            return (priority + count, len(word))

        filtered_words.sort(key=sort_key, reverse=True)
        return [word for word, count in filtered_words[:top_k]]

    def process_papers(self, papers):
        processed_data = []
        for paper in papers:
            clean_title = self.clean_html(paper.get('title', ''))
            clean_abstract = self.clean_html(paper.get('abstract', ''))
            combined_text = clean_title + ' ' + clean_abstract
            keywords = self.extract_keywords(combined_text, top_k=5)

            processed_paper = {
                'id': paper.get('id'),
                'title': clean_title,
                'abstract': clean_abstract,
                'publish_date': paper.get('publish_date'),
                'keywords': keywords,
                'text_for_vectorization': f"{clean_title}。{clean_abstract} 关键词：{', '.join(keywords)}"
            }
            processed_data.append(processed_paper)
        return processed_data

    def get_vectorization_format(self, processed_data):
        return [{
            'doc_id': paper['id'],
            'content': paper['text_for_vectorization'],
            'metadata': {
                'title': paper['title'],
                'publish_date': paper['publish_date'],
                'keywords': paper['keywords']
            }
        } for paper in processed_data]


# ==================== 2. 向量化引擎 ====================

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
            print("✅ 模型加载成功！\n")
        except ImportError:
            print("⚠️  未安装 sentence-transformers，使用模拟向量演示...")
            self.model = None

    def vectorize(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        if self.model_type == 'local' and self.model is not None:
            return self._vectorize_local(texts)
        else:
            return self._vectorize_mock(texts)

    def _vectorize_local(self, texts):
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    def _vectorize_mock(self, texts):
        """模拟向量化（用于演示，实际使用时请安装依赖）"""
        print("⚠️  使用模拟向量（随机生成），实际应用请安装 sentence-transformers")
        # 生成768维的模拟向量（与text2vec-base-chinese维度一致）
        np.random.seed(42)
        return np.random.randn(len(texts), 768).astype(np.float32)

    def _vectorize_api(self, texts):
        """API向量化示例（OpenAI/智谱）"""
        # OpenAI示例
        # import openai
        # openai.api_key = self.api_key
        # response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
        # return np.array([item['embedding'] for item in response['data']])

        # 智谱AI示例
        # from zhipuai import ZhipuAI
        # client = ZhipuAI(api_key=self.api_key)
        # response = client.embeddings.create(model="embedding-2", input=texts)
        # return np.array([item.embedding for item in response.data])

        raise NotImplementedError("API方案需要配置密钥，请参考代码注释")

    def similarity_search(self, query, corpus_embeddings, corpus_data, top_k=3):
        query_embedding = self.vectorize([query])
        similarities = cosine_similarity(query_embedding, corpus_embeddings)[0]
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


# ==================== 3. 运行完整流程 ====================

print("=" * 70)
print("🔬 医学文献处理 + 向量化系统")
print("=" * 70)

# 原始数据
papers = [
    {"id": "001", "title": "糖尿病治疗方案研究",
     "abstract": "<p>本研究探讨了<b>糖尿病</b>患者的治疗方案，对比了胰岛素治疗和口服药物的效果。</p>",
     "publish_date": "2024-01-15"},
    {"id": "002", "title": "高血压的临床诊断",
     "abstract": "<p>本文总结了<b>高血压</b>的临床诊断标准，分析了高血压患者的病因和风险因素。</p>",
     "publish_date": "2024-02-20"},
    {"id": "003", "title": "心脏病预防指南",
     "abstract": "<p>心脏病是威胁人类健康的主要疾病。本文介绍了心脏病的预防方法，包括饮食控制、运动锻炼。</p>",
     "publish_date": "2024-03-10"}
]

# 步骤1: 数据预处理
print("\n【步骤1】数据清洗与关键词提取...")
processor = MedicalLiteratureProcessor()
processed_papers = processor.process_papers(papers)
vectorization_data = processor.get_vectorization_format(processed_papers)

print(f"✅ 完成！处理文献数: {len(vectorization_data)}")
for item in vectorization_data:
    print(f"  📄 {item['doc_id']}: {item['metadata']['title']}")
    print(f"     关键词: {', '.join(item['metadata']['keywords'])}")

# 步骤2: 向量化
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
    print(f"\n  文献 {item['doc_id']}: {item['metadata']['title']}")
    print(f"    向量形状: {emb.shape}")
    print(f"    前5维: [{', '.join([f'{x:.4f}' for x in emb[:5]])}]")
    print(f"    L2范数: {np.linalg.norm(emb):.4f}")
    print(f"    存储大小: {emb.nbytes} 字节 ({emb.nbytes / 1024:.2f} KB)")

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
        print(f"  排名{res['rank']}: [{res['doc_id']}] {res['title']}")
        print(f"           相似度: {res['similarity']:.4f}")
        print(f"           关键词: {', '.join(res['keywords'])}")

print("\n" + "=" * 70)
print("✅ 完整流程演示结束！")
print("=" * 70)

# 展示向量化的数学原理和存储格式

print("📐 向量化原理说明：")
print("=" * 60)
print("""
1. 文本 → 向量的转换过程：

   输入文本: "糖尿病治疗方案研究。本研究探讨了糖尿病患者..."
      ↓
   Tokenizer分词: [糖, 尿病, 治疗, 方案, ...]  
      ↓
   Embedding层: 每个token转换为768维向量
      ↓
   池化(Pooling): 取均值 → 得到句子向量 [768维]
      ↓
   归一化: L2归一化使向量长度为1，便于计算余弦相似度

2. 相似度计算（余弦相似度）：

   similarity = cos(θ) = (A·B) / (||A|| × ||B||)

   值域: [-1, 1]，通常文本相似度在 [0, 1] 之间
   越接近1表示语义越相似

3. 向量存储格式示例（JSON）：
""")

# 生成一个完整的存储示例
storage_example = {
    "corpus_id": "medical_papers_v1",
    "embedding_model": "text2vec-base-chinese",
    "embedding_dim": 768,
    "papers": []
}

for i, item in enumerate(vectorization_data):
    storage_example["papers"].append({
        "doc_id": item['doc_id'],
        "title": item['metadata']['title'],
        "keywords": item['metadata']['keywords'],
        "publish_date": item['metadata']['publish_date'],
        "content_preview": item['content'][:50] + "...",
        "embedding": {
            "dim": 768,
            "dtype": "float32",
            "values_sample": corpus_embeddings[i][:5].tolist(),  # 只展示前5维
            "storage_path": f"./embeddings/{item['doc_id']}.npy"
        }
    })

print(json.dumps(storage_example, ensure_ascii=False, indent=2))

print("\n" + "=" * 60)
print("💾 向量存储建议：")
print("=" * 60)
print("""
1. 小规模数据(<1万条): 
   - 使用numpy数组直接存储: np.save('embeddings.npy', embeddings)
   - 或使用pickle序列化

2. 中等规模数据(1万-100万条):
   - 使用向量数据库: FAISS, Annoy, Milvus Lite
   - 支持高效的相似度检索

3. 大规模数据(>100万条):
   - 专业向量数据库: Milvus, Pinecone, Weaviate, Qdrant
   - 支持分布式存储和近似最近邻(ANN)检索

4. 存储优化:
   - 量化(Quantization): float32 → float16/int8，减少50%-75%存储
   - 降维: PCA降至256维，减少2/3存储同时保持90%信息
""")

# 提供两种向量数据库的集成示例代码

vector_db_examples = '''
# ==================== 向量数据库集成示例 ====================

# 方案A: 使用 FAISS (Facebook AI Similarity Search)
# 安装: pip install faiss-cpu  或  pip install faiss-gpu

def init_faiss_index(embeddings):
    """
    初始化FAISS索引
    适用于百万级向量的高效检索
    """
    import faiss

    dim = embeddings.shape[1]  # 768维

    # 创建索引 (使用内积，因为向量已归一化，内积=余弦相似度)
    index = faiss.IndexFlatIP(dim)  # IP = Inner Product

    # 添加向量
    index.add(embeddings.astype('float32'))

    print(f"FAISS索引构建完成，包含 {index.ntotal} 个向量")
    return index

def faiss_search(index, query_embedding, vector_engine, k=5):
    """FAISS检索"""
    query_embedding = query_embedding.astype('float32')
    scores, indices = index.search(query_embedding, k)
    return scores[0], indices[0]


# 方案B: 使用 ChromaDB (轻量级，适合本地)
# 安装: pip install chromadb

def init_chroma_db(collection_name="medical_papers"):
    """
    初始化ChromaDB
    适合快速原型开发和中小规模数据
    """
    import chromadb
    from chromadb.config import Settings

    # 创建客户端
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./chroma_db"
    ))

    # 创建集合
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}  # 使用余弦距离
    )

    return collection

def add_to_chroma(collection, vectorization_data, embeddings):
    """添加数据到ChromaDB"""
    ids = [item['doc_id'] for item in vectorization_data]
    documents = [item['content'] for item in vectorization_data]
    metadatas = [item['metadata'] for item in vectorization_data]

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=documents,
        metadatas=metadatas
    )
    print(f"已添加 {len(ids)} 篇文献到ChromaDB")

def chroma_search(collection, query_embedding, n_results=3):
    """ChromaDB检索"""
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )
    return results


# 方案C: 使用 Milvus (企业级)
# 安装: pip install pymilvus

def init_milvus_collection(collection_name="medical_papers"):
    """
    初始化Milvus集合
    适合大规模生产环境
    """
    from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

    # 连接Milvus
    connections.connect("default", host="localhost", port="19530")

    # 定义字段
    fields = [
        FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=50, is_primary=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="publish_date", dtype=DataType.VARCHAR, max_length=20),
    ]

    # 创建集合
    schema = CollectionSchema(fields, "医学文献向量库")
    collection = Collection(collection_name, schema)

    # 创建索引 (IVF_FLAT是平衡性能和精度的选择)
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    collection.create_index("embedding", index_params)

    return collection


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 假设已有: vectorization_data, corpus_embeddings

    # 1. FAISS示例
    print("=== FAISS 示例 ===")
    faiss_index = init_faiss_index(corpus_embeddings)

    # 查询
    query = "糖尿病治疗方法"
    query_emb = vector_engine.vectorize([query])
    scores, indices = faiss_search(faiss_index, query_emb, k=3)

    print(f"查询: {query}")
    for score, idx in zip(scores[0], indices[0]):
        print(f"  相似度: {score:.4f}, 文献: {vectorization_data[idx]['metadata']['title']}")

    # 保存索引
    faiss.write_index(faiss_index, "medical_papers.index")

    # 2. ChromaDB示例
    print("\\n=== ChromaDB 示例 ===")
    chroma_collection = init_chroma_db()
    add_to_chroma(chroma_collection, vectorization_data, corpus_embeddings)

    results = chroma_search(chroma_collection, query_emb, n_results=3)
    print(f"查询结果: {results}")
'''

print(vector_db_examples)

print("\\n" + "=" * 70)
print("📦 完整系统架构总结")
print("=" * 70)
print("""
┌─────────────────────────────────────────────────────────────────┐
│                     医学文献处理系统架构                          │
├─────────────────────────────────────────────────────────────────┤
│  输入层: 原始JSON数据 (含HTML标签的医学文献)                       │
│     ↓                                                           │
│  预处理层: MedicalLiteratureProcessor                           │
│     ├─ 数据清洗: clean_html() → 去除HTML标签和特殊字符            │
│     ├─ 关键词提取: extract_keywords() → 词典+n-gram词频统计       │
│     └─ 数据转换: get_vectorization_format() → 结构化数据          │
│     ↓                                                           │
│  向量化层: VectorizationEngine                                  │
│     ├─ 本地模型: sentence-transformers (text2vec-base-chinese)   │
│     ├─ API方案: OpenAI/智谱/文心等Embedding接口                   │
│     └─ 输出: 768维浮点向量                                       │
│     ↓                                                           │
│  存储层: 向量数据库 (可选)                                         │
│     ├─ 轻量级: FAISS, ChromaDB (万级数据)                        │
│     └─ 企业级: Milvus, Pinecone (百万级+数据)                    │
│     ↓                                                           │
│  应用层: 相似度检索、智能问答、文献推荐                            │
│     └─ similarity_search() → 余弦相似度 + Top-K排序              │
└─────────────────────────────────────────────────────────────────┘
""")

# 最终：提供可直接运行的完整代码文件内容

complete_system_code = '''"""
医学文献处理与向量化系统 (Medical Literature Processing & Vectorization System)

功能模块:
1. 数据清洗: 去除HTML标签、特殊字符
2. 关键词提取: 基于医学词典 + n-gram词频统计  
3. 文本向量化: 支持本地模型(sentence-transformers)或API
4. 相似度检索: 余弦相似度计算 + Top-K排序

依赖安装:
    pip install sentence-transformers numpy scikit-learn

可选依赖(向量数据库):
    pip install faiss-cpu  # 或 faiss-gpu
    pip install chromadb
    pip install pymilvus
"""

import json
import re
import numpy as np
from collections import Counter
from typing import List, Dict, Union, Tuple
from sklearn.metrics.pairwise import cosine_similarity


class MedicalLiteratureProcessor:
    """
    医学文献预处理器

    功能:
    - HTML标签清洗
    - 医学关键词提取（词典优先 + n-gram补充）
    - 数据格式转换
    """

    def __init__(self):
        # 停用词表
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
            '介绍', '威胁', '人类', '健康', '对比了', '总结了', '探讨了'
        }

        # 医学术语词典（按长度降序，确保优先匹配长词）
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
            '临床试验', '随机对照', '双盲试验', '安慰剂', '疗效评估', '副作用'
        ]
        # 按长度降序排序，确保优先匹配"胰岛素治疗"而非"胰岛素"+"治疗"
        self.medical_terms.sort(key=len, reverse=True)

    def clean_html(self, text: str) -> str:
        """
        清洗HTML标签和特殊字符

        Args:
            text: 原始文本（可能包含<p>, <b>等HTML标签）

        Returns:
            清洗后的纯文本
        """
        if not text:
            return ""

        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)

        # 去除HTML实体 (&nbsp;, &lt;等)
        text = re.sub(r'&[a-zA-Z]+;', ' ', text)
        text = re.sub(r'&#[0-9]+;', ' ', text)

        # 去除特殊字符，保留中文、英文、数字和基本标点
        text = re.sub(r'[^\\u4e00-\\u9fa5a-zA-Z0-9\\s，。；：！？、""''（）]', ' ', text)

        # 合并多个空格
        text = re.sub(r'\\s+', ' ', text)

        return text.strip()

    def extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """
        提取医学关键词

        策略:
        1. 医学术语词典匹配（优先长词）
        2. 剩余文本进行n-gram分词（2-4字）
        3. 停用词过滤 + 词频统计
        4. 按优先级排序（医学术语优先）

        Args:
            text: 输入文本
            top_k: 返回前k个关键词

        Returns:
            关键词列表
        """
        if not text:
            return []

        keywords = []
        remaining_text = text

        # 步骤1: 医学术语词典匹配（最大匹配）
        for term in self.medical_terms:
            if term in remaining_text:
                count = remaining_text.count(term)
                keywords.extend([term] * count)
                # 用空格替换已匹配的术语，避免被n-gram切开
                remaining_text = remaining_text.replace(term, ' ')

        # 步骤2: n-gram分词（对剩余文本，2-4字）
        def get_ngrams(s: str, n: int) -> List[str]:
            """生成n-gram"""
            return [s[i:i+n] for i in range(len(s)-n+1)]

        # 只保留中文字符进行n-gram
        chinese_text = re.sub(r'[^\\u4e00-\\u9fa5]', '', remaining_text)

        ngram_words = []
        for n in range(4, 1, -1):  # 从4字到2字，优先长词
            ngrams = get_ngrams(chinese_text, n)
            for gram in ngrams:
                if (gram not in self.stop_words and 
                    not re.match(r'^\\d+$', gram) and
                    len(gram) >= 2):
                    ngram_words.append(gram)

        # 步骤3: 合并并统计词频
        all_keywords = keywords + ngram_words
        word_counts = Counter(all_keywords)

        # 步骤4: 过滤和排序
        filtered_words = []
        for word, count in word_counts.items():
            if word in self.stop_words:
                continue
            # 过滤停用词字符占比过高的词
            stop_char_ratio = sum(1 for c in word if c in '的了和是在有与及之') / len(word)
            if stop_char_ratio > 0.5:
                continue
            filtered_words.append((word, count))

        # 排序策略: 医学术语优先，其次按词频，再按词长
        def sort_key(item):
            word, count = item
            is_medical_term = word in self.medical_terms
            priority = 1000 if is_medical_term else 0  # 医学术语加权
            return (priority + count, len(word))

        filtered_words.sort(key=sort_key, reverse=True)

        return [word for word, count in filtered_words[:top_k]]

    def process_papers(self, papers: List[Dict]) -> List[Dict]:
        """
        批量处理文献

        Args:
            papers: 文献列表，每项包含id, title, abstract, publish_date

        Returns:
            处理后的文献列表，包含清洗后的文本和提取的关键词
        """
        processed_data = []

        for paper in papers:
            # 清洗HTML
            clean_title = self.clean_html(paper.get('title', ''))
            clean_abstract = self.clean_html(paper.get('abstract', ''))

            # 提取关键词（结合标题和摘要）
            combined_text = clean_title + ' ' + clean_abstract
            keywords = self.extract_keywords(combined_text, top_k=5)

            # 构建向量化文本（整合所有信息）
            text_for_vectorization = f"{clean_title}。{clean_abstract} 关键词：{', '.join(keywords)}"

            processed_paper = {
                'id': paper.get('id'),
                'title': clean_title,
                'abstract': clean_abstract,
                'publish_date': paper.get('publish_date'),
                'keywords': keywords,
                'text_for_vectorization': text_for_vectorization
            }
            processed_data.append(processed_paper)

        return processed_data

    def get_vectorization_format(self, processed_data: List[Dict]) -> List[Dict]:
        """
        转换为向量化标准格式

        Args:
            processed_data: process_papers的输出

        Returns:
            适合向量化的结构化数据，包含doc_id, content, metadata
        """
        return [{
            'doc_id': paper['id'],
            'content': paper['text_for_vectorization'],
            'metadata': {
                'title': paper['title'],
                'publish_date': paper['publish_date'],
                'keywords': paper['keywords']
            }
        } for paper in processed_data]


class VectorizationEngine:
    """
    向量化引擎

    支持多种向量化方案:
    - 本地模型: sentence-transformers (推荐: text2vec-base-chinese)
    - API方案: OpenAI, 智谱AI, 文心一言等
    """

    def __init__(self, model_type: str = 'local', model_name: str = None, api_key: str = None):
        """
        初始化向量化引擎

        Args:
            model_type: 'local' 或 'api'
            model_name: 本地模型名称或API模型名称
            api_key: API密钥（仅model_type='api'时需要）
        """
        self.model_type = model_type
        self.model = None
        self.model_name = model_name
        self.api_key = api_key

        if model_type == 'local':
            self._init_local_model()

    def _init_local_model(self):
        """初始化本地sentence-transformers模型"""
        try:
            from sentence_transformers import SentenceTransformer

            # 默认使用轻量级中文模型
            model_name = self.model_name or 'shibing624/text2vec-base-chinese'
            print(f"🔄 加载本地模型: {model_name}...")

            self.model = SentenceTransformer(model_name)
            print(f"✅ 模型加载成功！输出维度: {self.model.get_sentence_embedding_dimension()}")

        except ImportError:
            raise ImportError("请先安装sentence-transformers: pip install sentence-transformers")

    def vectorize(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        将文本转换为向量

        Args:
            texts: 单个字符串或字符串列表

        Returns:
            numpy数组，shape: (n_samples, embedding_dim)
        """
        if isinstance(texts, str):
            texts = [texts]

        if self.model_type == 'local':
            return self._vectorize_local(texts)
        else:
            return self._vectorize_api(texts)

    def _vectorize_local(self, texts: List[str]) -> np.ndarray:
        """使用本地模型向量化"""
        embeddings = self.model.encode(
            texts, 
            convert_to_numpy=True, 
            show_progress_bar=False,
            normalize_embeddings=True  # L2归一化，便于计算余弦相似度
        )
        return embeddings

    def _vectorize_api(self, texts: List[str]) -> np.ndarray:
        """
        使用API向量化（示例代码，需配置密钥）

        支持:
        - OpenAI: model="text-embedding-ada-002"
        - 智谱AI: model="embedding-2"
        """
        raise NotImplementedError(
            "API向量化需要配置密钥。请参考以下示例实现:\\n"
            "OpenAI示例:\\n"
            "  import openai; openai.api_key = 'your-key'\\n"
            "  response = openai.Embedding.create(input=texts, model='text-embedding-ada-002')\\n"
            "  return np.array([item['embedding'] for item in response['data']])"
        )

    def similarity_search(
        self, 
        query: str, 
        corpus_embeddings: np.ndarray, 
        corpus_data: List[Dict], 
        top_k: int = 3
    ) -> List[Dict]:
        """
        相似度检索

        Args:
            query: 查询文本
            corpus_embeddings: 语料库向量矩阵 (n_docs, embedding_dim)
            corpus_data: 原始语料数据（用于返回元信息）
            top_k: 返回最相似的k个结果

        Returns:
            相似度排序后的结果列表，包含doc_id, title, similarity, keywords
        """
        # 向量化查询
        query_embedding = self.vectorize([query])

        # 计算余弦相似度（向量已归一化，点积=余弦相似度）
        similarities = cosine_similarity(query_embedding, corpus_embeddings)[0]

        # 获取top_k索引
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # 构建结果
        results = []
        for rank, idx in enumerate(top_indices, 1):
            results.append({
                'rank': rank,
                'doc_id': corpus_data[idx]['doc_id'],
                'title': corpus_data[idx]['metadata']['title'],
                'similarity': float(similarities[idx]),
                'keywords': corpus_data[idx]['metadata']['keywords']
            })

        return results


class MedicalLiteratureSystem:
    """
    医学文献处理系统（整合版）

    使用示例:
        system = MedicalLiteratureSystem()

        # 1. 处理文献
        vector_data = system.process(papers)

        # 2. 向量化
        embeddings = system.vectorize()

        # 3. 检索
        results = system.search("糖尿病治疗方法")
    """

    def __init__(self, model_type='local', model_name=None):
        self.processor = MedicalLiteratureProcessor()
        self.vector_engine = VectorizationEngine(model_type, model_name)
        self.corpus_data = None
        self.corpus_embeddings = None

    def process(self, papers: List[Dict]) -> List[Dict]:
        """处理原始文献数据"""
        processed = self.processor.process_papers(papers)
        self.corpus_data = self.processor.get_vectorization_format(processed)
        return self.corpus_data

    def vectorize(self) -> np.ndarray:
        """对处理后的文献进行向量化"""
        if not self.corpus_data:
            raise ValueError("请先调用process()处理文献数据")

        texts = [item['content'] for item in self.corpus_data]
        self.corpus_embeddings = self.vector_engine.vectorize(texts)
        return self.corpus_embeddings

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """相似度检索"""
        if self.corpus_embeddings is None:
            raise ValueError("请先调用vectorize()生成向量")

        return self.vector_engine.similarity_search(
            query, self.corpus_embeddings, self.corpus_data, top_k
        )


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例数据
    papers = [
        {
            "id": "001",
            "title": "糖尿病治疗方案研究",
            "abstract": "<p>本研究探讨了<b>糖尿病</b>患者的治疗方案，对比了胰岛素治疗和口服药物的效果。</p>",
            "publish_date": "2024-01-15"
        },
        {
            "id": "002", 
            "title": "高血压的临床诊断",
            "abstract": "<p>本文总结了<b>高血压</b>的临床诊断标准，分析了高血压患者的病因和风险因素。</p>",
            "publish_date": "2024-02-20"
        },
        {
            "id": "003",
            "title": "心脏病预防指南",
            "abstract": "<p>心脏病是威胁人类健康的主要疾病。本文介绍了心脏病的预防方法，包括饮食控制、运动锻炼。</p>",
            "publish_date": "2024-03-10"
        }
    ]

    # 初始化系统
    system = MedicalLiteratureSystem(model_type='local')

    # 完整流程
    print("=" * 60)
    print("医学文献处理与向量化系统")
    print("=" * 60)

    # 1. 处理
    print("\\n【1】数据预处理...")
    corpus_data = system.process(papers)
    print(f"✅ 处理完成，共 {len(corpus_data)} 篇文献")

    # 2. 向量化
    print("\\n【2】文本向量化...")
    embeddings = system.vectorize()
    print(f"✅ 向量化完成，维度: {embeddings.shape}")

    # 3. 检索
    print("\\n【3】相似度检索演示:")
    queries = ["胰岛素治疗糖尿病", "高血压诊断方法", "心脏病预防"]

    for query in queries:
        print(f"\\n查询: '{query}'")
        results = system.search(query, top_k=2)
        for res in results:
            print(f"  排名{res['rank']}: [{res['doc_id']}] {res['title']}")
            print(f"           相似度: {res['similarity']:.4f}")
'''

print(complete_system_code)

# 生成最终总结报告

print("=" * 80)
print("📋 医学文献处理系统 - 完整实现总结")
print("=" * 80)

print("""
✅ 已实现的功能模块:

1️⃣  数据清洗 (MedicalLiteratureProcessor.clean_html)
    • 去除HTML标签 (<p>, <b>, <div>等)
    • 处理HTML实体 (&nbsp;, &lt;等)
    • 过滤特殊字符，保留中文/英文/数字/基本标点
    • 规范化空格

2️⃣  关键词提取 (MedicalLiteratureProcessor.extract_keywords)  
    • 医学术语词典匹配（优先长词匹配）
    • n-gram分词补充（2-4字，剩余文本）
    • 停用词过滤 + 词频统计
    • 优先级排序（医学术语优先）

3️⃣  文本向量化 (VectorizationEngine.vectorize)
    • 本地模型: sentence-transformers (text2vec-base-chinese, 768维)
    • API支持: OpenAI, 智谱AI等（预留接口）
    • 自动L2归一化，优化余弦相似度计算

4️⃣  相似度检索 (VectorizationEngine.similarity_search)
    • 余弦相似度计算
    • Top-K排序返回
    • 支持批量查询

📦 系统架构:
┌──────────────────────────────────────────────────────────────────────┐
│  MedicalLiteratureSystem (整合入口)                                   │
│  ├─ MedicalLiteratureProcessor (数据清洗 + 关键词提取)                │
│  └─ VectorizationEngine (向量化 + 相似度检索)                         │
└──────────────────────────────────────────────────────────────────────┘

🔧 使用方式:

方式一: 快速使用（推荐）
    system = MedicalLiteratureSystem()
    corpus_data = system.process(papers)      # 预处理
    embeddings = system.vectorize()            # 向量化
    results = system.search("查询文本")         # 检索

方式二: 分步使用（更灵活）
    processor = MedicalLiteratureProcessor()
    processed = processor.process_papers(papers)
    vector_data = processor.get_vectorization_format(processed)

    engine = VectorizationEngine()
    embeddings = engine.vectorize([item['content'] for item in vector_data])
    results = engine.similarity_search(query, embeddings, vector_data)

📥 依赖安装:
    pip install sentence-transformers numpy scikit-learn

💾 向量存储扩展（可选）:
    pip install faiss-cpu    # Facebook相似度检索库
    pip install chromadb     # 轻量级向量数据库
    pip install pymilvus     # 企业级向量数据库
""")

print("=" * 80)
print("📝 完整代码已提供，可直接保存为 .py 文件运行")
print("=" * 80)
