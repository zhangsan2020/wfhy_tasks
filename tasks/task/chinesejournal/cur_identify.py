import os
import re
import fitz
from .word_transfrom import WordTrans
from ..common.log import FrameLog

class CurIdentify():

    def __init__(self):

        self.wordtrans = WordTrans()
        self.log = FrameLog('yii').get_log()

    def identify_pdf(self, file_path):

        items = {'doctor_info': [], 'phones': []}
        try:
            pdf = fitz.open(file_path)
            for page in pdf.pages():
                text = page.get_text("text")
                if text:
                    data = self.wordtrans.stringQ2B(text)
                    if re.findall('(作者.*?:.*)', data):
                        # print('要看的数据: ',re.findall('(作者.*?:.*)', data))
                        items['doctor_info'].extend(re.findall('(作者.*?:.*\n.*)', data))
                    if re.findall('1[356789]\d{9}\d{0,5}', data):
                        phones = re.findall('1[356789]\d{9}\d{0,5}', data)
                        print('疑似手机号为: ', re.findall('1[356789]\d{9}\d{0,5}', data))
                        for phone in phones:
                            if len(phone) == 11:
                                print('恭喜你! 发现真实手机号一枚: {}'.format(phone))
                                self.log.info('恭喜你! 发现真实手机号一枚: {} 文件路径为: {}'.format(phone,file_path))
                                items['phones'].append(phone)
                            else:
                                print('识别出号码长度过长, 为 {} 位, 确认不是真手机号, 舍去!!'.format(len(phone)))
                                self.log.info('识别出号码长度过长, 为 {} 位, 确认不是真手机号, 舍去!!,路径地址为: {}'.format(len(phone),file_path))
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
                items['phones'] = '/'.join(list(set(items['phones'])))
            else:
                items['phones'] = ''
            items['identify_status'] = '识别成功'
        except Exception as e:
            print('识别文件时出错...')
            print(repr(e))
            items['identify_status'] = '识别失败'
            items['doctor_info'] = ''
            items['phones'] = ''
        return items

if __name__ == '__main__':
    # 对糖尿病肾脏疾病湿热证患者与正常人群尿液外泌体微RNA差异表达的研究.pdf
    # file_path = r'E:/zhihu_pdfs/new/慢性乙型肝炎临床热点问题解析.pdf'
    # file_path = 'E:/zhihu_pdfs/基于Nrf2_Keap1信号通路研究黄芩甲苷对糖尿病肾病小鼠肾损伤的作用.pdf'
    file_path = 'F:/weipu_pdfs/老年患者日间手术全程质量管理模式研究2022.pdf'
    identify = CurIdentify()
    identify.identify_pdf(file_path)
