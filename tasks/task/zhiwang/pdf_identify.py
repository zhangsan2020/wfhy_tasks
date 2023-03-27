
import re
from word_transfrom import WordTrans
import pdfplumber
import os

dir_path = 'E:/zhihu_pdfs/new/'
wordtrans = WordTrans()


for root, dirs, files in os.walk(dir_path+'/.'):
    for file in files:
        file_name, file_kind = os.path.splitext(file)
        print(file)
        if file_kind == '.pdf':
            file_path = os.path.join(dir_path, file)
            print('当前文件为: ',file_path)
            # file_path = r'E:\zhihu_pdfs\基于lncRNA测序探讨瑞舒伐他汀对糖尿病大鼠心肌损伤的治疗途径和潜在靶点.pdf'
            pdf_file = open(file_path,'rb')
            try:
                # pdf = open()
                pdf = pdfplumber.open(pdf_file)
                # 1. 把所有页的数据存在一个临时列表中
                item = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        data = wordtrans.stringQ2B(text)
                        if re.findall('(作者.*?:.*)',data):
                            item.extend(re.findall('(作者.*?:.*)',data))
                        if re.findall('1[3-9]\d{9}\d{0,10}', data):
                            print('疑似手机号为: ',re.findall('1[3-9]\d{9}\d{0,10}', data))
                            item.extend(re.findall('1[3-9]\d{9}\d{0,10}', data))
                        if re.findall('(E-mail.*?:.*)', data):
                           print('邮箱为: ', re.findall('(E-mail.*?:.*)', data))
                           item.extend(re.findall('(E-mail.*?:.*)', data))
                    else:
                        print('当前页没有文本信息')
                if item:
                    print(item)
                    print('识别结果为:  ',set(item))
                pdf.close()
                pdf_file.close()
            except Exception as e:
                pdf_file.close()
                print('文件出错')
                print(repr(e))
                # new_name = os.path.join(dir_path, '00_' + file)
                # os.rename(file_path,new_name)