import json
import random
import re
import time
import requests
import ddddocr
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



class LoginTrun():

    def __init__(self,owning_account):

        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.img_code_path = 'F:/wanfang_tasks/tasks/task/yiigle/yiigle_spider/{}_code.jpg'.format(owning_account)
        # self.domain = 'http://www.sinomed.a.fg77.club/'


    def get_code_headers(self):

        headers_code_1 = {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    "Host": "www.90tsg.com",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
                }
        headers_code_2 = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
                }
        headers_list = [headers_code_1,headers_code_2]
        header_code = random.choice(headers_list)
        return header_code

    def get_img_data(self):

        img_url = 'http://www.90tsg.com/e/ShowKey/?v=login'
        headers_code = self.get_code_headers()
        print('当前验证码请求头为: ',headers_code)
        self.session.cookies.clear()
        res = self.session.get(img_url, headers = headers_code,timeout=(10,20))
        with open(self.img_code_path, 'wb') as f:
            f.write(res.content)
            f.close()

    def recognize_img(self):

        ocr = ddddocr.DdddOcr()
        with open(self.img_code_path, 'rb') as f:
            img_bytes = f.read()
            f.close()
        code_num = ocr.classification(img_bytes)
        print(code_num)
        return code_num



    def selenium_login(self):

        chrome_options = Options()
        # 把Chrome设置成无界面模式
        chrome_options.headless = True
        self.driver = webdriver.Chrome(options=chrome_options)
        url = 'http://www.90tsg.com/e/member/login/'
        for i in range(10):
            print('开始使用selenium进行第 {} 次登录'.format(i))
            try:
                self.driver.get(url)
                time.sleep(random.uniform(30,40))
                self.driver.find_element(By.ID, 'username').send_keys('00966849')
                self.driver.find_element(By.ID, 'password').send_keys('971152')
                self.driver.find_element(By.NAME, 'Submit').click()
                print('第 {} 登录中 点击提交完成!! 请等待40秒, 查看登录状态!!'.format(i))
                time.sleep(60)
                if '您身边的数字图书馆' in self.driver.page_source:
                    print('90tsg 登录成功!!')
                    cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
                    print('获取到最新cookies为: ',cookies)
                    print('开始重置session中错误的cookies')
                    self.session.cookies.update(cookies)
                    print('这是session中的cookies', self.session.cookies)
                    self.driver.close()
                    return 'selenium_success'
                else:
                    print('通过selenium登录后未出现登录成功!! 稍等3~5分钟, 重新登录')
                    time.sleep(random.uniform(5,10))
            except Exception as e:
                print('使用selenium登录出现异常第 {} 次 : {}'.format(i,repr(e)))
                print('通过selenium登录时出现错误!! 稍等1~2分钟, 重新登录')
                time.sleep(random.uniform(60, 120))

    def login_tsg(self):

        headers = {
                "Host": "www.90tsg.com",
                "Connection": "keep-alive",
                "Content-Length": "107",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "Origin": "http://www.90tsg.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Referer": "http://www.90tsg.com/e/member/login/",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }

        login_url = 'http://www.90tsg.com/e/member/doaction.php'
        for i in range(20):
            try:
                data = {
                    'ecmsfrom': '',
                    'enews': 'login',
                    'tobind': 0,
                    'username': '00966849',
                    'password': '971152',
                    'lifetime': 0,
                    'Submit': '登    录'
                }
                res = self.session.post(login_url, data=data, headers=headers, timeout=(180, 360))

                if res.status_code == 200 and '登录成功' in res.text:
                    print('90图书馆登录成功!!')
                    return 1
                else:
                    print('登录90tsg时返回数据异常, 稍等一会儿, 重新发起登录请求!!!')
                    print(res.text)
                    time.sleep(random.uniform(10, 20))
                    self.session.cookies.clear()
            except:
                print('登录90tsg时出错, 稍等一会儿, 重新发起登录请求!!!')
                time.sleep(random.uniform(6, 12))
                self.session.cookies.clear()

            print('连续第 {} 次登录出现异常'.format(i))
            if i >= 1:
                print('连续登录出现异常超过 2 次,等待2~3分钟时间, 开始使用 selenium 重新登录')
                time.sleep(random.uniform(10,15))
                # self.session.get('http://www.90tsg.com/e/member/login/',headers=headers_again)
                print('开始清理session中错误的cookies!!')
                self.session.cookies.clear()
                status = self.selenium_login()
                if status == 'selenium_success':
                    print('通过selenium登录成功!!')
                    break


    def login_page_turn(self,owning_account):

        # self.domains = ['www-sinomed-ac-cn.njmu.jitui.me','www.sinomed.a.fg77.club']
        for i in range(10):
            self.login_tsg()
            cookies = self.session.cookies.get_dict()
            self.session.cookies.clear_session_cookies()
            self.session.cookies.update(cookies)
            data = {
                'siteid': 'www.90tsg.com&uname={}&uid={}'.format(cookies['noiojmlusername'], cookies['noiojmluserid'])
            }
            # self.domain = self.domains[0]
            # print('当前域名为: {}'.format(self.domain))
            if owning_account == '6849_南京医科大学':
                headers = {
                        "Host": 'www-sinomed-ac-cn.njmu.jitui.me',
                        "Connection": "keep-alive",
                        "Content-Length": "46",
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": "http://www.90tsg.com",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                res = self.session.post('http://www-sinomed-ac-cn.njmu.jitui.me/index.jsp', data=json.dumps(data),headers=headers)
                # print(res.text)
                if res.status_code == 200 and '中国生物医学文献服务系统' in res.text:
                    print('成功进入中国生物医学文献服务系统,当前是 6849_南京医科大学 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入中国生物医学文献服务系统失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(2,5))
                    # with open('失败.html','w',encoding='utf-8') as f:
                    #     f.write(res.text)
                    #     f.close()
                    if i >= 5:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
                    # self.domains.reverse()
            #     华中科技大学同济医学院
            elif owning_account == '6849_华中科技大学同济医学院':
                # self.domains = ['www-sinomed-ac-cn.njmu.jitui.me','www.sinomed.a.fg77.club']

                headers = {
                        "Host": "www.sinomed.a.fg77.club",
                        "Connection": "keep-alive",
                        "Content-Length": "46",
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": "http://www.90tsg.com",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                res = self.session.post('http://www.sinomed.a.fg77.club/index.jsp', data=json.dumps(data),headers=headers)
                # print(res.text)
                if res.status_code == 200 and '中国生物医学文献服务系统' in res.text:
                    print('成功进入中国生物医学文献服务系统,当前是 6849_华中科技大学同济医学院 账号')
                    # print(res.text)

                    return self.session
                else:
                    print('当前第 {} 次进入中国生物医学文献服务系统失败, 休息一下, 继续登录!'.format(i))

                    time.sleep(random.uniform(2, 5))
                    if i >= 5:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600, 900))
                    # self.domains.reverse()
            elif owning_account == '6849_南方科技大学':
                headers = {
                    "Host": "fjykdxnshfsfljsbhfkew883sdjfns.98tsg.com",
                    "Connection": "keep-alive",
                    "Content-Length": "44",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Content-Type": "application/json",
                    "Origin": "http://fjykdxnshfsfljsbhfkew883sdjfns.98tsg.com",
                    "Referer": "http://fjykdxnshfsfljsbhfkew883sdjfns.98tsg.com/",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
                data_login = {"condition": {"loginName": "", "password": ""}}
                res = self.session.post('http://fjykdxnshfsfljsbhfkew883sdjfns.98tsg.com/getCore/pcLogin',
                                        data=json.dumps(data_login),
                                        headers=headers)
                print(res.text)
                if res.status_code == 200 and res.json()['success'] == True:
                    print('成功进入中华医学网,当前是 6849_南方科技大学 账号')
                    return self.session, res.json()
                else:
                    print('当前第 {} 次登录中华医学网失败, 继续登录!'.format(i))
                    time.sleep(2)
            elif owning_account == '6849_浙江中医药大学':
                headers = {
                    "Host": "zdcsxylsrijgoieurjhgfo.98tsg.com",
                    "Connection": "keep-alive",
                    "Content-Length": "44",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Content-Type": "application/json",
                    "Origin": "http://zdcsxylsrijgoieurjhgfo.98tsg.com",
                    "Referer": "http://zdcsxylsrijgoieurjhgfo.98tsg.com/",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
                data_login = {"condition": {"loginName": "", "password": ""}}
                res = self.session.post('http://zdcsxylsrijgoieurjhgfo.98tsg.com/getCore/pcLogin',
                                        data=json.dumps(data_login),
                                        headers=headers)
                print(res.text)
                if res.status_code == 200 and res.json()['success'] == True:
                    print('成功进入中华医学网,当前是 6849_浙江中医药大学 账号')
                    return self.session, res.json()
                else:
                    print('当前第 {} 次登录中华医学网失败, 继续登录!'.format(i))
                    time.sleep(2)
            elif owning_account == '443_jitui':
                print(self.session.cookies)
                url1 = 'http://www.90tsg.com/e/action/ShowInfo.php?classid=185&id=2513'
                headers_1 = {
                        "Host": "www.90tsg.com",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Referer": "http://www.90tsg.com/e/action/ListInfo/?classid=185",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                res = self.session.get(url1,headers=headers_1)
                # print('这是cookies: ',res.cookies)
                url2 = 'https://www-yiigle-com-443--ccmu.jitui.me/index'
                headers_2 = {
                        "Host": "www-yiigle-com-443--ccmu.jitui.me",
                        "Connection": "keep-alive",
                        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Sec-Fetch-Site": "cross-site",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Dest": "document",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                # print('---'*20)
                res = self.session.get(url2,headers=headers_2)
                print('这是cookies: ',res.cookies)
                print('这是总的cookies: ',self.session.cookies)
                # res = self.session.get(url2,headers=headers_2)
                # print('这是cookies: ',res.cookies)
                # print('这是总的cookies: ',self.session.cookies)
                # print('---'*20)
                url4 = 'http://www.90tsg.com/e/action/ShowInfo.php?classid=185&id=2514'
                headers_4 = {
                            "Host": "www.90tsg.com",
                            "Connection": "keep-alive",
                            "Upgrade-Insecure-Requests": "1",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                            "Referer": "http://www.90tsg.com/e/action/ListInfo/?classid=185",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "zh-CN,zh;q=0.9"
                        }
                res = self.session.get(url4,headers=headers_4)

                url3 = 'https://www-yiigle-com-443--ccmu.jitui.me/apiVue/affiche/list'
                headers_3 = {
                            "Host": "www-yiigle-com-443--ccmu.jitui.me",
                            "Connection": "keep-alive",
                            "Content-Length": "0",
                            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                            "Accept": "application/json, text/plain, */*",
                            "sec-ch-ua-mobile": "?0",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                            "sec-ch-ua-platform": "\"Windows\"",
                            "Origin": "https://www-yiigle-com-443--ccmu.jitui.me",
                            "Sec-Fetch-Site": "same-origin",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Dest": "empty",
                            "Referer": "https://www-yiigle-com-443--ccmu.jitui.me/index",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "zh-CN,zh;q=0.9"
                        }
                res = self.session.post(url3,headers=headers_3)
                print('届时的cookies: ',self.session.cookies)
                url = 'https://www-yiigle-com-443--ccmu.jitui.me/apiVue/index/getUserInfo'
                headers = {
                        "Host": "www-yiigle-com-443--ccmu.jitui.me",
                        "Connection": "keep-alive",
                        "Content-Length": "49",
                        "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                        "Accept": "application/json, text/plain, */*",
                        "Content-Type": "application/json;charset=UTF-8",
                        "sec-ch-ua-mobile": "?0",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "token": "[object Object]",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "Origin": "https://www-yiigle-com-443--ccmu.jitui.me",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Dest": "empty",
                        "Referer": "https://www-yiigle-com-443--ccmu.jitui.me/index",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        # "Cookie": "ddhgguuy_session=6m3stm67pepml1tvuk23q4alr7; Hm_lvt_086e860fd41dcb45bb007e07a0961bd8=1674885862; JSESSIONID_CACHE=3EAC5B1484B856ACE5EA0CF9019FFCE6; Hm_lpvt_086e860fd41dcb45bb007e07a0961bd8=1674886964; AWSALB=//pvSjYEz4cMTmYCVZIOPqPR51HAvRCwehsZ0j0ZrsWxLtxc7IM4TjH03v94jIcOIgOuF9pWLqr6Fm/b6SfgsiA+RuEdfUirtMltF+yBCGX8F1Wnn6r1tuWwFHFA; AWSALBCORS=//pvSjYEz4cMTmYCVZIOPqPR51HAvRCwehsZ0j0ZrsWxLtxc7IM4TjH03v94jIcOIgOuF9pWLqr6Fm/b6SfgsiA+RuEdfUirtMltF+yBCGX8F1Wnn6r1tuWwFHFA"
                    }
                data = {"logintoken":"855169b956c043ee9ab98ee44891001b"}
                res = self.session.post(url,headers=headers,data=json.dumps(data))
                print(res.text)
                break
                pass
            elif owning_account == '6849_山东大学':
                url = 'http://www.90tsg.com/e/action/ShowInfo.php?classid=185&id=2514'
                headers = {
                    "Host": "www.90tsg.com",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Referer": "http://www.90tsg.com/e/action/ListInfo/?classid=185",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
                res = self.session.get(url, headers=headers)
                print(res.text)
                url_list = re.findall('obj.action		=	"(.*?)"',res.text)
                print('这是截取的url: ',url_list)
                if url_list:
                    url = url_list[0]
                    headers = {
                            "Host": "sdu.jitui.me",
                            "Connection": "keep-alive",
                            "Content-Length": "46",
                            "Cache-Control": "max-age=0",
                            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                            "sec-ch-ua-mobile": "?0",
                            "sec-ch-ua-platform": "\"Windows\"",
                            "Upgrade-Insecure-Requests": "1",
                            "Origin": "http://www.90tsg.com",
                            "Content-Type": "application/x-www-form-urlencoded",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                            "Sec-Fetch-Site": "cross-site",
                            "Sec-Fetch-Mode": "navigate",
                            "Sec-Fetch-Dest": "document",
                            "Referer": "http://www.90tsg.com/",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "zh-CN,zh;q=0.9"
                        }
                    res = self.session.post(url,headers=headers,data=json.dumps(data))
                    print(res.text)
                    print(res.url)
                    if res.status_code == 200 and '__vpn_hostname_data' in res.text:
                        print('进入中华医学会成功, 当前是山东大学账号')
                        break
                    else:
                        print('当前是第 {} 次登录未进入到 中华医学会'.format(i))
            elif owning_account == '6849_扬州大学':
                url = 'http://www.yiigle.yz.jd314.vip/index'
                headers = {
                        "Host": "www.yiigle.yz.jd314.vip",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                print('第一次请求获取cookie!!')
                self.session.get(url,headers=headers)
                print('第二次请求继续获取cookie!!')
                res = self.session.get(url, headers=headers)
                print(res.text)
                print(self.session.cookies)
                headers = {
                            "Host": "www.yiigle.yz.jd314.vip",
                            "Connection": "keep-alive",
                            "Content-Length": "49",
                            "Accept": "application/json, text/plain, */*",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                            "token": "[object Object]",
                            "Content-Type": "application/json;charset=UTF-8",
                            "Origin": "http://www.yiigle.yz.jd314.vip",
                            "Referer": "http://www.yiigle.yz.jd314.vip/index",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "zh-CN,zh;q=0.9",
                            # "Cookie": "ddhgguuy_session=pnttq26b59q2fvvgl85nodjmr4; Hm_lvt_086e860fd41dcb45bb007e07a0961bd8=1674970843,1675066577; JSESSIONID=D94EF16C192F1A259C6C22C45F6C1224; JSESSIONID_CACHE=D94EF16C192F1A259C6C22C45F6C1224; Hm_lpvt_086e860fd41dcb45bb007e07a0961bd8=1675126365; AWSALB=qckJPRhd39WHBJaYcNiIHws4Z+Y3hgb63oaapYgVF1KCl7MQHyefwjzXyrMo9CwgSX0UYRC5GA+w0Q+iQELtIWcML3kYQ4ggsqGafTARKwdrICToZQWztp1tEG6R"
                        }
                data = {"logintoken":"dab5c1409f0c495bb3a3076bc8206d88"}
                url = 'http://www.yiigle.yz.jd314.vip/apiVue/index/getUserInfo'
                res = self.session.post(url,json=data,headers=headers)
                print(res.text)
                if res.status_code == 200 and '操作成功' in res.text:
                    print('进入中学医学期刊数据库,当前是扬州大学账号!!')
                    return self.session,res.json()
                else:
                    print('账号 {} , 当前第 {} 次登录中华医学网失败, 继续登录!'.format(owning_account,i))
                    time.sleep(2)

# login = LoginTrun('6849_南京医科大学')
# login.login_page_turn('6849_南京医科大学')
