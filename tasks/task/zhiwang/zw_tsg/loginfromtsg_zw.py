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

        headers = {
                    # "Host": "tsg211.com",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Referer": "http://tsg211.com/e/action/ShowInfo.php?classid=68&id=2254",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
               }

        rr = self.session.get('http://tsg211.com/zhyxhsd.php',headers=headers, timeout=(10,20))
        rr.encoding = 'utf-8'
        # print('这是进入中文期刊服务平台的text: ',rr.text)
        print('这是跳转之后的页面数据: ',rr.text)
        # time.sleep(10)
        # if 'sdu.webvpn.jingshi2015' in rr.text:
        #     print('跳转成功, 已进入 中文期刊服务平台')
        #     print('这是要看的链接地址!!',rr.url)
        #     return rr.url
        # else:
        #     print('跳转到其它地方, 重新发起跳转请求!!')
        #     time.sleep(2)
        #     return self.turn_url()

    def login_page_turn(self):

        self.login_tsg()
        print(self.session.cookies)
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
        res = self.session.get('http://tsg211.com/e/action/ListInfo/?classid=61',headers=headers)
        # html = etree.HTML(res.text)
        # wp_link = html.xpath('//a[text()="维普3"]/@href')[0]
        # link = 'http://tsg211.com' + wp_link
        # print(link)
        link = 'http://tsg211.com/e/action/ShowInfo.php?classid=62&id=1952'
        self.headers_turn = {
            "Host": "tsg211.com",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://tsg211.com/e/member/doaction.php",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cookie": "ujgpvmlusername=71014289; ujgpvmluserid=163708; ujgpvmlgroupid=10; ujgpvmlrnd=Uk0lSi297B8qGauVIeYZ; ujgpvmlauth=a8d9e1e2ebc9c051f39e937021539d59"
        }


        url_css = 'http://tsg211.com/css/plan.css'
        headers = {
                        "Host": "tsg211.com",
                        "Connection": "keep-alive",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                        "Accept": "text/css,*/*;q=0.1",
                        "Referer": "http://tsg211.com/e/action/ListInfo/?classid=61",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        # "Cookie": "ujgpvpayphome=BuyGroupPay; ujgpvmlusername=71014289; ujgpvmluserid=163708; ujgpvmlgroupid=10; ujgpvmlrnd=wAJcPkPOfGAwb2GTreRX; ujgpvmlauth=f1ea46474640d0967646a27570d41603"
                    }
        res = self.session.get(url_css,headers=headers)
        print('css连接返回数据为: ',res.text)

        headres_0 = {
                        "Host": "tsg211.com",
                        "Connection": "keep-alive",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                        "Accept": "*/*",
                        "Referer": "http://tsg211.com/e/action/ListInfo/?classid=61",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
        url_0 = 'http://tsg211.com/e/member/login/520loginjs.php'
        res = self.session.get(url_0,headers=headres_0)
        print('这是要看的: ',res.text)
        headers_1 = {
                    "Host": "tsg211.com",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Referer": "http://tsg211.com/e/action/ListInfo/?classid=61",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
        r = self.session.get(link,headers=headers_1)
        html = etree.HTML(r.text)
        username = html.xpath('//input[@name="FrontLoginForm[username]"]/@value')[0]
        password = html.xpath('//input[@name="FrontLoginForm[password]"]/@value')[0]
        rememberMe = html.xpath('//input[@name="LoginForm[rememberMe]"]/@value')[0]
        login_button = html.xpath('//input[@name="login-button"]/@value')[0]
        print('这是数据: ',username,password,rememberMe,login_button)

        url_1 = 'http://login.fafu.vpn358.com/index.php?pre=http%3A%2F%2Fwww.cnki.net.fafu.vpn358.com'
        data = {
            "FrontLoginForm[username]":"000Q819032",
            "FrontLoginForm[password]":"YlDO0ITM",
            "LoginForm[rememberMe]":"062015",
            "login-button":"062015"
        }
        headers = {
            "Host": "login.fafu.vpn358.com",
            "Connection": "keep-alive",
            "Content-Length": "130",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "Origin": "http://tsg211.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://tsg211.com/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cookie": "vpn358_tips=1sp1gk6be8hed4o8g5dultmfou"
        }
        res = self.session.post(url_1,data=data,headers=headers)
        print(res.text)
        print(res.url)
        # print(r.text)
        # print(r.url)
        headers_2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }
        res = self.session.get('http://www.cnki.net.fafu.vpn358.com/',headers=headers_2)
        res.encoding = 'utf-8'
        print(res.text)
        if '文献来源' in res.text:
            print('已进入知网')
        else:
            print('没有进入知网, 可重新获取')
            time.sleep(3)
            self.login_page_turn()

# login = LoginTrun()
# login.login_page_turn()
