import json
import pdfplumber
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

# 使用 UTF-8 编码打开 JSON 文件
with open("questions.json", encoding='utf-8') as file:
    questions = json.load(file)
print(questions[0])

# 打开 PDF 文件并处理
pdf = pdfplumber.open("data.pdf")
print("Total pages:", len(pdf.pages))  # 打印总页数
first_page_text = pdf.pages[0].extract_text()  # 读取第一页内容
print("First page text:", first_page_text)  # 打印第一页的内容

# 初始化空列表用于存储每页的内容
pdf_content = []
for page_idx in range(len(pdf.pages)):
    page_text = pdf.pages[page_idx].extract_text()
    pdf_content.append({
        'page': 'page_' + str(page_idx + 1),
        'content': page_text
    })

# 对提问和PDF内容进行分词
question_words = [' '.join(jieba.lcut(x['question'])) for x in questions]
pdf_content_words = [' '.join(jieba.lcut(x['content'])) for x in pdf_content]

tfidf = TfidfVectorizer()
tfidf.fit(question_words + pdf_content_words)

# 提取TFIDF
question_feat = tfidf.transform(question_words)
pdf_content_feat = tfidf.transform(pdf_content_words)

# 进行归一化
question_feat = normalize(question_feat)
pdf_content_feat = normalize(pdf_content_feat)

# 检索进行排序
for query_idx, feat in enumerate(question_feat):
    score = feat @ pdf_content_feat.T
    score = score.toarray()[0]
    # 获取最高分的前十个索引
    top_10_indices = score.argsort()[-10:][::-1] + 1  # 使用[::-1]来反转，得到最大的10个值
    questions[query_idx]['top_references'] = ['page_' + str(idx) for idx in top_10_indices]

# 生成提交结果
with open('submit_top10_short.json', 'w', encoding='utf8') as up:
    json.dump(questions, up, ensure_ascii=False, indent=4)
