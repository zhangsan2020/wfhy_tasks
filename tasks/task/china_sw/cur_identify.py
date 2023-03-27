import os
import re
import fitz
from PIL import Image
# from pytesseract import pytesseract
import pytesseract
from .word_transfrom import WordTrans
# from ..common.log import FrameLog

class CurIdentify():

    def __init__(self):

        self.wordtrans = WordTrans()
        # self.log = FrameLog('yii').get_log()

    def check_phone(self,data):

        phones = []
        phones_data = [phone for phone in re.findall('([1|86][135678]\d+)', data) if len(phone) >= 11]
        if phones_data:
            for phone in phones_data:
                if '86' in phone and len(phone) == 13 and re.findall('861[3578]\d{9}', phone):
                    print('当前手机号符号86格式的特征: ', phone)
                    phones.append(phone)
                    # print('类似手机号存在于数字中, 但数字过长, 大概率不是手机号, 跳过!!')
                elif len(phone) == 11 and re.findall('1[3578]\d{9}', phone):
                    print('当前手机号符合正常手机号特征! ', phone)
                    phones.append(phone)
                    # print('类似手机号存在于数字中, 但数字过长, 大概率不是手机号, 跳过!!')
                else:
                    print('当前手机号不符合手机号特征', phone)
        return phones

    def identify_pdf(self, file_path):

        items = {'doctor_info': [],'phones':[]}
        try:
            pdf = fitz.open(file_path)
            for page in pdf.pages():
                text = page.get_text("text")
                if text:
                    data = self.wordtrans.stringQ2B(text)
                    if re.findall('(作者.*?:.*)', data):
                        # print('要看的数据: ',re.findall('(作者.*?:.*)', data))
                        items['doctor_info'].extend(re.findall('(作者.*?:.*\n.*)', data))
                        items['phones'] = self.check_phone(data)
                    # re.findall('(1[35678]\d{9})[^.\d]', data)
                    # if re.findall('(1[35678]\d{9})', data):
                    #     phones = re.findall('(1[35678]\d{9})', data)
                    #     print('疑似手机号为: ', re.findall('(1[35678]\d{9})', data))
                        # print('这是phones数据: ',phones)
                        # for phone in phones:
                        #     if len(phone) == 11:
                        #         print('恭喜你! 发现真实手机号一枚: {}'.format(phone))
                        #         # self.log.info('恭喜你! 发现真实手机号一枚: {} 文件路径为: {}'.format(phone,file_path))
                        #         items['phones'].append(phone)
                        #     else:
                        #         print('识别出号码长度过长, 为 {} 位, 确认不是真手机号, 舍去!!'.format(len(phone)))
                                # self.log.info('识别出号码长度过长, 为 {} 位, 确认不是真手机号, 舍去!!,路径地址为: {}'.format(len(phone),file_path))
                    # if re.findall('(E-mail.*?:.*)', data):
                    #     print('邮箱为: ', re.findall('(E-mail.*?:.*)', data))
                    #     item.extend(re.findall('(E-mail.*?:.*)', data))
                else:
                    print('当前页没有文本信息')
            pdf.close()
            if items['doctor_info']:
                items['doctor_info'] = str(items['doctor_info'])
            else:
                items['doctor_info'] = ''
            if items['phones']:
                items['phones'] = list(set(items['phones']))
            else:
                items['phones'] = ''
            items['identify_status'] = '识别成功'
        except Exception as e:
            print('识别文件时出错...')
            print(repr(e))
            # self.log.warning('识别文件时出错... 路径为: {}, 错误信息为: {}'.format(file_path,repr(e)))
            # new_name = file_path.replace('.pdf','_失败.pdf')
            # try:
            #     os.rename(file_path, new_name)
            # except Exception as e:
            #     self.log.warning('pdf文件改名失败,不在继续进行修改!!, info: {}'.format(repr(e)))
            #     print('pdf文件改名失败,不在继续进行修改!!, info: {}'.format(repr(e)))
            items['identify_status'] = '识别失败'
            items['doctor_info'] = ''
            items['phones'] = ''
        return items

    def extract_text(self,file_name):
        extract_text = ''  # 用于存储提取的文本
        doc = fitz.open(file_name)
        # 遍历每一页pdf
        print('pages:', len(doc))
        for i in range(len(doc)):
            img_list = doc.get_page_images(i)  # 提取该页中的所有img
            print(img_list)
            print(len(img_list))
            for num, img in enumerate(img_list):
                img_name = "C:/Users/hello/Desktop/2023年提交数据/{}{}.png".format(i+1,num+1)  # 存储的图片名
                pix = fitz.Pixmap(doc, img[0])  # image转pixmap
                if pix.n - pix.alpha >= 4:  # 如果差值大于等于4，需要转化后才能保存为png
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(img_name)  # 存储图片
                pix = None  # 释放Pixmap资源
                image = Image.open(img_name)
                text = pytesseract.image_to_string(image,'chi_sim')  # 调用tesseract，使用中文库，要求库文件放在C:\Program Files (x86)\Tesseract-OCR目录想
                print(text)
                extract_text += text  # 写入文本
                os.remove(img_name)
        print(extract_text)
            # return extract_text

if __name__ == '__main__':
    # 对糖尿病肾脏疾病湿热证患者与正常人群尿液外泌体微RNA差异表达的研究.pdf
    # file_path = r'E:/zhihu_pdfs/new/慢性乙型肝炎临床热点问题解析.pdf'
    # file_path = 'E:/zhihu_pdfs/基于Nrf2_Keap1信号通路研究黄芩甲苷对糖尿病肾病小鼠肾损伤的作用.pdf'
    file_path = 'F:/weipu_pdfs/老年患者日间手术全程质量管理模式研究2022.pdf'
    identify = CurIdentify()
    identify.identify_pdf(file_path)
