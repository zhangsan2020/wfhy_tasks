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

    def turn_url(self):

        rr = self.session.get('http://tsg211.com/weipu.php',headers=self.headers_turn, timeout=20)
        # for one_info in rr.history:
        #     print(one_info.status_code, one_info.url, one_info.headers)
        print(rr.text)
        if 'jiangnan.webvpn' in rr.text:
            print('跳转成功, 已进入 中文期刊服务平台')
            print('这是要看的链接地址!!',rr.url)
            return rr.url
            # print(rr.text)
        else:
            print('跳转到其它地方, 重新发起跳转请求!!')
            # print(rr.text)
            time.sleep(10)
            return self.turn_url()

    def login_page_turn(self):

        self.login_tsg()
        res = self.session.get('http://tsg211.com/e/action/ListInfo/?classid=61')
        html = etree.HTML(res.text)
        wp_link = html.xpath('//a[text()="维普3"]/@href')[0]
        link = 'http://tsg211.com' + wp_link
        print(link)
        self.headers_turn = {
            # "Host": "tsg211.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://tsg211.com/e/action/ListInfo/?classid=61",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "ujgpvmlusername=71014289; ujgpvmluserid=163708; ujgpvmlgroupid=10; ujgpvmlrnd=Uk0lSi297B8qGauVIeYZ; ujgpvmlauth=a8d9e1e2ebc9c051f39e937021539d59"
        }
        # print(self.session.cookies)
        # 第一种添加cookie 的方式
        # cookies_part = {
        #     "Hm_lvt_04b5e4d6892791247a01f35935d692be":"1670286856,1670291708",
        #     "authdomain":"AuthDomain.tsg211.com",
        #     "ujgpvpayphome":"BuyGroupPay",
        #     "Hm_lpvt_04b5e4d6892791247a01f35935d692be":"1670306448"
        # }
        # requests.utils.add_dict_to_cookiejar(self.session.cookies, cookies_part)
        # 第二种添加cookie的方式
        # self.session.cookies.set(name="Hm_lvt_04b5e4d6892791247a01f35935d692be",value="1670286856,1670291708",domain=".tsg211.com")
        # self.session.cookies.set(name="authdomain",value="AuthDomain.tsg211.com",domain=".tsg211.com")
        # self.session.cookies.set(name="ujgpvpayphome",value="BuyGroupPay",domain=".tsg211.com")
        # self.session.cookies.set(name="Hm_lpvt_04b5e4d6892791247a01f35935d692be",value="1670306448",domain=".tsg211.com")
        # # print(self.session.cookies)
        r = self.session.get(link,headers=self.headers_turn)
        # # print(self.session.request)
        self.headers_turn['Referer']= link
        self.login_after_url = self.turn_url()
        return self.session
# login = LoginTrun()
# login.login_page_turn()
