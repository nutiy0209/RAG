import json
import pdfplumber
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# 加载预训练模型
model = SentenceTransformer("moka-ai/m3e-base")
print("Model loaded.")

# 连接到 Elasticsearch
es = Elasticsearch(['http://localhost:9200'])
print("Connected to Elasticsearch.")

# 获取用户输入
user_query = input("Please enter your question: ")
print("User question received.")

# 对用户问题进行处理
# 注意：这里假设用户的问题可以直接用模型处理。根据需要，您可能需要额外处理文本。
user_query_embedding = model.encode([user_query], normalize_embeddings=True)
print('Embeddings generated for user query.')

# 准备将处理结果存入 Elasticsearch 的数据
action = {
    "_index": "user_queries",  # 可以是专门存储用户查询的新索引
    "_source": {
        "query_text": user_query,
        "query_vector": user_query_embedding[0].tolist()  # 假设我们只处理了一个问题
    }
}
print("Data prepared for indexing.")

# 使用 helpers.bulk() 批量上传，这里因为只有一个文档，我们可以直接用 index
es.index(index="user_queries", document=action['_source'])
print("Data has been indexed to Elasticsearch.")
