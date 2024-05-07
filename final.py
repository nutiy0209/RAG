import json
import pdfplumber
import time 
import jwt
import requests
import numpy as np

# 实际KEY，过期时间
def generate_token(apikey: str, exp_seconds: int):
    try:
        id, secret = apikey.split(".")
    except Exception as e:
        raise Exception("invalid apikey", e)

    payload = {
        "api_key": id,
        "exp": int(round(time.time() * 1000)) + exp_seconds * 1000,
        "timestamp": int(round(time.time() * 1000)),
    }
    return jwt.encode(
         payload,
        secret,
        algorithm="HS256",
        headers={"alg": "HS256", "sign_type": "SIGN"},
    )
#定義調用glm
def ask_glm(content) : 
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
    'Content-Type': 'application/json',
    'Authorization': generate_token("f6b379cbf6902ef7860483a7fd20456d.yYIN3hlgMt1oiYG1", 10000000)
    }

    data = {
        "model": "glm-3-turbo",
        "messages": [{"role": "user", "content": content}]
    }

    response = requests.post(url, headers=headers, json=data)
    print("[大模型返回]")
    print(response)
    return response.json()

m3e = json.load(open('m3e_top_10.json', encoding='utf-8'))  # 指定编码为 UTF-8
bm25 = json.load(open('submit_top10.json', encoding='utf-8'))

# m3e = json.load(open('m3e_top_10.json'))
# bm25 = json.load(open('submit_top10.json'))

question = json.load(open("questions.json", encoding='utf-8'))
pdf = pdfplumber.open("data.pdf")
pdf_content_dict = {}
for page_idx in range(len(pdf.pages)):
    pdf_content_dict['page_' + str(page_idx + 1)] = pdf.pages[page_idx].extract_text()

fusion_result = []
k = 60 
for q1, q2 in zip(m3e[:], bm25[:]):
    fusion_score = {}
    for idx, q in enumerate(q1['references']):
        if q not in fusion_score:
            fusion_score[q] = 1 / (idx + k)      
        else:
            fusion_score[q] += 1 / (idx + k)

    for idx, q in enumerate(q2['top_references']):
        if q not in fusion_score:
            fusion_score[q] = 1 / (idx + k)
        else:
            fusion_score[q] += 1 / (idx + k)

    sorted_dict = sorted(fusion_score.items(), key=lambda item: item[1], reverse=True)
    
    if not sorted_dict:
        print("未找到有效的参考页面")
        continue  # 或者选择合适的默认值或错误处理逻辑
    q1['references'] = sorted_dict[0][0]

    reference_pages = [int(x[0].split('_')[1]) for x in sorted_dict]
    reference_pages = np.array(reference_pages)

    reference_content = ''
    # 循环获取每个页面的内容并构建 reference_content 字符串
    for page_number in reference_pages:
        page_key = 'page_' + str(page_number)  # 正确的键格式
        if page_key in pdf_content_dict:
            reference_content += pdf_content_dict[page_key] + '\n'  # 添加该页的内容
    reference_content += "上述內容在第" + str(reference_pages) + "頁。"  # 添加页码信息

    print("user question \n" + q1["question"])
    print("參考資料 \n" + pdf_content_dict[q1['references']])

    reference_page = q1['references'].split('_')[1]

    prompt = '''你是一位汽車專家，幫我結合給定的資料，回答下面的問題，如果問題無法從資料中獲得，或無法從資料中進行回答，請回答無法回答，如果可以回答，請結合資料集進行回答
資料: {0}



問題: {1}
    '''.format(reference_content,q1["question"])
    #answer = ask_glm(prompt)['choices'][0]['message']['content']

    answer = '無法'
    for _ in range(5):
        try:
            answer = ask_glm(prompt)['choices'][0]['message']['content']
            if answer:
                break
        except:
            print('111')
            continue

    if '無法' in answer:
        answer = '結合給定的資料無法進行回答'

    q1['answer'] = answer
    print("模型返回 \n" + q1['answer'])

    print("\n\n\n")

    fusion_result.append(q1)

with open('submit_m3e+bm25+glm.json', 'w', encoding='utf8') as up:
    json.dump(fusion_result, up, ensure_ascii=False, indent=4)