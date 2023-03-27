import re
import time

import ddddocr
import requests
from requests.adapters import HTTPAdapter
from PIL import Image, ImageEnhance


class CmeLogin():

    # def __init__(self,session):
    #     # self.session = requests.Session()
    #     # self.session.mount('http://', HTTPAdapter(max_retries=3))
    #     # self.session.mount('https://', HTTPAdapter(max_retries=3))
    #     self.session = session
    def get_img_data(self):

        time_ = int(time.time() * 1000)
        img_url = 'https://cmegsb.cma.org.cn/national_project/CheckCodeImageServlet?r={}'.format(time_)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        }
        res = self.session.get(img_url, headers=headers)
        with open('cme_code.jpg', 'wb') as f:
            f.write(res.content)

    def recognize_img(self):
        ocr = ddddocr.DdddOcr(det=False)
        # with open('cme_code.jpg', 'rb') as f:
        #     img_bytes = f.read()
        im2 = self.clear_img()
        # im2.show()
        code_num = ocr.classification(im2)
        print(code_num)
        return code_num

    def clear_img(self):
        # import pytesseract
        # tesseract_cmd = r'C:\Program Files\Tesseract-OCR'
        # pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        # 上面都是导包，只需要下面这一行就能实现图片文字识别
        im = Image.open('cme_code.jpg')
        # 下面为增强部分
        enh_con = ImageEnhance.Contrast(im)
        contrast = 2
        image_contrasted = enh_con.enhance(contrast)
        # image_contrasted.show()

        # 增强亮度
        enh_bri = ImageEnhance.Brightness(image_contrasted)
        brightness = 1.5
        image_brightened = enh_bri.enhance(brightness)
        # image_brightened.show()
        # 增强对比度
        enh_col = ImageEnhance.Color(image_brightened)
        color = 1.5
        image_colored = enh_col.enhance(color)
        # image_colored.show()
        # 增强锐度
        enh_sha = ImageEnhance.Sharpness(image_colored)
        sharpness = 3
        image_sharped = enh_sha.enhance(sharpness)
        # image_sharped.show()
        # 灰度处理部分
        im2 = image_sharped.convert("L")
        return im2

    def calculate(self,data,mode):
        if mode == '加':
            return sum(data)
        elif mode == '减':
            return data[0] - data[1]
        elif mode == '乘':
            return data[0] * data[1]
        elif mode == '除':
            return data[0] // data[1]
        else:
            print('计算模式不对, 请重新获取验证码处理计算!!')

    def isChinese(self,words):

        for ch in words:
            if '\u4e00' <= ch <= '\u9fff':
                return ch
        return False

    def login(self,session):

        self.session = session
        for i in range(20):
            self.get_img_data()
            code_str = self.recognize_img()
            if '加' in code_str or '减' in code_str or '乘' in code_str or '除' in code_str:
                mode = self.isChinese(code_str)
                # print('这是计算方式: ',mode)
                nums = []
                num_list = re.findall('(\d+)',code_str)
                print('这是获取到的所有的数字列表: ',num_list)
                if len(num_list) > 1:
                    for num_data in num_list:
                        # print('这是 num_data',num_data)
                        if int(num_data) > 10:
                            print('切割数字, 留下前一位做计算!!')
                            num_data = num_data[0]
                        nums.append(int(num_data))
                    print('识别信息为: {} {} {} = ?'.format(nums[0],mode,nums[1]))
                    res = self.calculate(nums,mode)
                    if res:
                        print('当前计算结果为: ',res)
                        return self.session,res
                    else:
                        print('计算发生异常, 大概率是计算模式识别错误! 重新发起验证码识别!!!')
                        continue
                else:
                    print('验证码识别计算数字的前或者后一个数字未识别到, 重新获取识别')
                    continue
            else:
                print('加减乘除符号没有识别出来, 重新获取识别')

# if __name__ == '__main__':
#
#     cme = CmeLogin()
#     cme.login()
    # cme.clear_img()