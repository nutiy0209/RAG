import json
import pdfplumber
from sentence_transformers import SentenceTransformer
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# 打开 PDF 文件并处理
pdf = pdfplumber.open("data.pdf")
print("Total pages:", len(pdf.pages))

pdf_content = []
for page_idx, page in enumerate(pdf.pages):
    page_text = page.extract_text()  # 提取文本
    pdf_content.append({
        'page': 'page_' + str(page_idx + 1),
        'content': page_text  # 存储页面文本
    })

# 加载预训练模型
model = SentenceTransformer("moka-ai/m3e-base")
print("debug1")

# 准备PDF内容句子
pdf_content_sentences = [x['content'] for x in pdf_content]
print("debug2")

# 计算句子嵌入向量，并进行归一化
pdf_embeddings = model.encode(pdf_content_sentences, normalize_embeddings=True)
print('Embeddings generated')
print("debug3")

# 连接到 Elasticsearch
es = Elasticsearch(['http://localhost:9200'])
# 打印Elasticsearch集群信息，检查是否连接成功
print(es.info())

# 准备数据
actions = []
for idx, content in enumerate(pdf_content):
    action = {
        "_index": "pdf_vectors",  # 索引名称
        "_source": {
            "content_vector": pdf_embeddings[idx].tolist(),  # 向量数据
            "id": idx + 1,  # 页码
            "page_number": idx + 1,  # 页码
            "text": content['content']  # 页面文本
        }
    }
    actions.append(action)

print("debug5")

# 使用 helpers.bulk() 批量上传
bulk(es, actions)
print("Data has been indexed to Elasticsearch")
