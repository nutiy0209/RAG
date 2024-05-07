import json
import pdfplumber

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

# 可以打印或处理 pdf_content 以进一步使用 PDF 中提取的数据
