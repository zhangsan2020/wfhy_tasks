import random
import time
import requests
from requests.adapters import HTTPAdapter
from task.common.useragent import useragent_pool
from task.zhiwang.zw_common import user_info
import ddddocr
from task.common.log import FrameLog

class ZwLogin():

    def __init__(self):

        self.headers_init = {
            'User-Agent': random.choice(useragent_pool)
        }
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.log = FrameLog('zw_cnki').get_log()

    def get_userinfo(self):
        userinfo = random.choice(user_info)
        return userinfo

    def get_checkcode(self, img):
        ocr = ddddocr.DdddOcr(old=True)
        # 第一个验证截图保存：verification_code_1.png
        with open(img, 'rb') as f:
            image = f.read()
        res = ocr.classification(image)
        return res

    def login(self):

        for i in range(20):
            print('当前是第 {} 次验证码识别'.format(i))
            user_agent = random.choice(useragent_pool)
            self.headers_init['User-Agent'] = user_agent
            time.sleep(1)
            userinfo = self.get_userinfo()
            print('当前用户信息为: ', userinfo)
            username = userinfo['username']
            password = userinfo['password']
            imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
            self.log.info('请求并识别验证码!!')
            res = self.session.get(imgcode_url, headers=self.headers_init, timeout=(5, 20))
            with open('imgcode.jpg', 'wb') as f:
                f.write(res.content)
            code_str = self.get_checkcode('imgcode.jpg')
            print('验证码字符串为: ', code_str)
            self.log.info('验证码识别结果为: {}'.format(code_str))
            time_ = int(time.time() * 1000)
            url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&checkCode={}&p=0&_={}'.format(
                username, password, code_str, time_)
            res = self.session.get(url, headers=self.headers_init, timeout=(5, 20))
            if '验证码不正确' in res.text:
                print('验证码识别失败,休息一下, 重新获取识别')
                time.sleep(2)
            elif '登录失败，没有该用户' in res.text:
                print('请确认账号密码!')
            elif '登录成功' not in res.text:
                print(res.text)
            else:
                print('登录成功!!')
                return self.session
            if i > 10:
                print('登录失败超过10次, 休息10min, 重新登录识别')
                time.sleep(300)