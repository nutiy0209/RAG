from elasticsearch import Elasticsearch

# 连接到 Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# 查询用户查询向量
user_query_id = "6LTpVI8B7eLbI18IXfI1"  # 假设您知道想要获取的查询ID
response = es.get(index="user_queries", id=user_query_id)
user_query_vector = response['_source']['query_vector']
user_query_text = response['_source']['query_text']  # 获取用户的查询文本

#print("Retrieved user query vector:", user_query_vector)

# 构建 script_score 查询
query = {
  "size": 1,  # 获取最相似的一个结果
  "query": {
    "script_score": {
      "query": {"match_all": {}},
      "script": {
        "source": "cosineSimilarity(params.query_vector, 'content_vector') + 1.0",  # 使用余弦相似度函数
        "params": {
          "query_vector": user_query_vector
        }
      }
    }
  }
}

# 执行查询
response = es.search(index="pdf_vectors", body=query)

# 打印结果
if response['hits']['hits']:
    hit = response['hits']['hits'][0]
    print("你是一位汽車專家，幫我結合給定的資料，回答下面的問題，如果問題無法從資料中獲得，或無法從資料中進行回答，請回答無法回答，如果可以回答，請結合資料集進行回答")
    print("資料:", hit['_source']['text'])  # 假设每个文档中都包含名为 'text' 的字段
    print("問題:", user_query_text)  # 假设每个文档中都包含名为 'text' 的字段
    print("Page Number:", hit['_source']['page_number'], "Score:", hit['_score'])
    
    
else:
    print("No similar pages found.")
