import time
import requests
import ddddocr
from lxml import etree
from requests.adapters import HTTPAdapter

class LoginTrun():

    def __init__(self):

        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def get_img_data(self):

        img_url = 'http://www.tsg211.com/e/ShowKey/?v=login'
        headers = {
            'Referer': 'http://www.tsg211.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        }
        res = self.session.get(img_url, headers=headers)
        with open('img_code.jpg', 'wb') as f:
            f.write(res.content)

    def recognize_img(self):

        ocr = ddddocr.DdddOcr()
        with open('./img_code.jpg', 'rb') as f:
            img_bytes = f.read()
        code_num = ocr.classification(img_bytes)
        print(code_num)
        return code_num

    def login_tsg(self):
        self.get_img_data()
        code_num = self.recognize_img()
        headers = {
            'Host': 'www.tsg211.com',
            'Origin': 'http://www.tsg211.com',
            'Pragma': 'no-cache',
            'Referer': 'http://www.tsg211.com/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        }
        login_url = 'http://www.tsg211.com/e/member/doaction.php'
        data = {
            'enews': 'login',
            'ecmsfrom': '/e/action/ListInfo/?classid=61',
            'username': '71014289',
            'password': '310233',
            'key': code_num,
            'ok': '立即登录'
        }
        res = self.session.post(login_url, data=data, headers=headers)
        # print(res.text)
        if '验证码不正确' in res.text:
            print('验证码识别错误, 重新登录')
            time.sleep(2)
            self.login_tsg()
        elif '登录成功' in res.text:
            print('tsg211图书馆登录成功!!')
            return 1

    def auth_success(self):

        auth_url = 'http://yixuehui.tsg211.com/yiigle/'
        data = {"condition": {"loginName": "", "password": ""}}
        headers = {
            "Host": "yixuehui.tsg211.com",
            "Connection": "keep-alive",
            "Content-Length": "44",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "http://yixuehui.tsg211.com",
            "Referer": "http://yixuehui.tsg211.com/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        res = self.session.post(auth_url, data=data, headers=headers)
        print(res.text)
        if res.status_code == 200 and '"success":true' in res.text:
            print('进入医学会成功')
            return res.json()

        else:
            print('进入医学会失败!!')
            time.sleep(3)
            return self.auth_success()

    def login_page_turn(self):

        self.login_tsg()
        cookies = self.session.cookies.get_dict()
        self.session.cookies.clear_session_cookies()
        self.session.cookies.update(cookies)
        headers = {
                    "Host": "tsg211.com",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Referer": "http://tsg211.com/e/member/doaction.php",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    # "Cookie": "ujgpvpayphome=BuyGroupPay; ujgpvmlusername=71014289; ujgpvmluserid=163708; ujgpvmlgroupid=10; ujgpvmlrnd=3jDEjWgXDBkslwdOzkfg; ujgpvmlauth=6f3d548dba81d2331569aed05154d1d7"
                }
        res = self.session.get('http://tsg211.com/e/action/ListInfo/?classid=66',headers=headers)

        link = 'http://tsg211.com/e/action/ShowInfo.php?classid=123&id=2025'
        r = self.session.get(link,headers=headers)
        json_data = self.auth_success()
        return self.session,json_data

# login = LoginTrun()
# login.login_page_turn()
