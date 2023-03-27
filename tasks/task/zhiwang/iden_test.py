import fitz
file_path = r'E:/zhihu_pdfs/垂体功能减退症合并肝硬化临床特征分析.pdf'
# file_path = 'E:/zhihu_pdfs/00_前路椎体骨化物复合体前移融合术治疗颈椎后纵韧带骨化症的研究进展.pdf'
# file_path = r'E:\zhihu_pdfs\基于网络药理学和实验验证探讨光甘草定治疗去势抵抗性前列腺癌的作用机制.pdf'
pdf = fitz.open(file_path)
print(pdf)
for page in pdf.pages():
    print(page)
    text = page.get_text("text")
    print(text.strip())