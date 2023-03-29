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
from task.chaoxing.chaoxing_spider.chaoxing_code import CxCode



class LoginTrun():

    def __init__(self,owning_account):

        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.img_code_path = '{}_code.jpg'.format(owning_account)
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

    def selenium_login_chaoxing(self,entry_name):
        chrome_options = Options()
        # 把Chrome设置成无界面模式
        chrome_options.headless = True
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--headless')
        url = 'http://www.90tsg.com/e/member/login/'
        for i in range(10):
            print('开始使用selenium进行第 {} 次登录'.format(i))
            self.driver = webdriver.Chrome(options=chrome_options)
            # self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            try:
                self.driver.get(url)
                time.sleep(random.uniform(5,10))
                self.driver.find_element(By.ID, 'username').send_keys('00966849')
                self.driver.find_element(By.ID, 'password').send_keys('971152')
                self.driver.find_element(By.NAME, 'Submit').click()
                print('第 {} 登录中 点击提交完成!! 请等待40秒, 查看登录状态!!'.format(i))
                time.sleep(10)
                if '您身边的数字图书馆' in self.driver.page_source:
                    print('90tsg 登录成功!!')
                    self.driver.find_element(By.XPATH,'//a[@title="超星数字"][1]').click()
                    time.sleep(random.uniform(5,10))
                    self.driver.find_element(By.XPATH,'//a[@title="{}"][1]'.format(entry_name)).click()
                    time.sleep(random.uniform(30,40))
                    window_handle = self.driver.window_handles  # 获取句柄
                    print("window_handle=", window_handle)
                    self.driver.switch_to.window(window_handle[-1])
                    time.sleep(random.uniform(10,20))
                    print(self.driver.page_source)
                    if '大雅相似度' in self.driver.page_source:
                        print('发现了 大雅相似度, 通过 selenium 成功进入超星期刊!!')
                        print('当前cookies为: ',self.driver.get_cookies())
                        if self.driver.get_cookies():
                            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
                            print('获取到最新cookies为: ',cookies)
                            print('开始重置session中错误的cookies')
                            self.session.cookies.update(cookies)
                            print('这是session中的cookies', self.session.cookies)
                            print('关闭 谷歌浏览器!!')
                            self.driver.quit()
                            time.sleep(5)
                            return 'selenium_success'
                        else:
                            print('发现cookies为 空, 重新登录获取!!')


                    elif '验证码错误' in self.driver.page_source or '您的操作出现异常，请输入验证码' in self.driver.page_source:
                        print('页面内出现了验证码, 在休息5~10min,继续登录!!')
                        time.sleep(random.uniform(300,600))
                    else:
                        print('通过 selenium 第 {}次 进入超星期刊失败, 继续进入!!'.format(i))
                        time.sleep(5)
                else:
                    print('通过selenium登录后未出现登录成功!! 稍等3~5分钟, 重新登录')
                    time.sleep(random.uniform(5,10))
            except Exception as e:
                print('使用selenium登录出现异常第 {} 次 : {}'.format(i,repr(e)))
                print('通过selenium登录时出现错误!! 稍等1~2分钟, 重新登录')
                time.sleep(random.uniform(60, 120))
            print('关闭 谷歌浏览器!!')
            self.driver.quit()
            time.sleep(5)

    def selenium_login_chinasw(self,entry_name):

        chrome_options = Options()
        # 把Chrome设置成无界面模式
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument("--window-size=1920,1080")
        # chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--headless')
        chrome_options.headless = True

        url = 'http://www.90tsg.com/e/member/login/'
        for i in range(10):
            print('开始使用selenium进行第 {} 次登录'.format(i))
            self.driver = webdriver.Chrome(options=chrome_options)
            # self.driver = webdriver.Chrome()
            self.driver.maximize_window()
            try:
                self.driver.get(url)
                time.sleep(random.uniform(30, 40))
                self.driver.find_element(By.ID, 'username').send_keys('00966849')
                self.driver.find_element(By.ID, 'password').send_keys('971152')
                self.driver.find_element(By.NAME, 'Submit').click()
                print('第 {} 登录中 点击提交完成!! 请等待40秒, 查看登录状态!!'.format(i))
                time.sleep(60)
                if '您身边的数字图书馆' in self.driver.page_source:
                    print('90tsg 登录成功!!')
                    self.driver.find_element(By.ID,'faqmenu').find_element(By.XPATH,'.//li[5]/a').click()
                    time.sleep(random.uniform(5,10))
                    self.driver.find_element(By.XPATH,'//a[@title="中国生物医学"]').click()
                    time.sleep(random.uniform(5,10))
                    self.driver.find_element(By.XPATH, '//a[@title="{}"]'.format(entry_name)).click()
                    time.sleep(random.uniform(30, 40))
                    window_handle = self.driver.window_handles  # 获取句柄
                    print("window_handle=", window_handle)
                    self.driver.switch_to.window(window_handle[-1])
                    time.sleep(random.uniform(10,20))
                    print(self.driver.page_source)
                    if '文献检索' in self.driver.page_source:
                        print('成功进入 中国生物医学文献系统!!')
                        print('这是cookies: ',self.driver.get_cookies())
                        # self.driver.find_element(By.XPATH,'')
                        print('开始刷新子页面')
                        time.sleep(2)
                        self.driver.refresh()
                        print('这是最新 cookies: ', self.driver.get_cookies())
                        if self.driver.get_cookies():
                            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}
                            print('获取到最新cookies为: ', cookies)
                            print('开始重置session中错误的cookies')
                            self.session.cookies.update(cookies)
                            print('这是session中的cookies', self.session.cookies)
                            time.sleep(random.uniform(1, 3))
                            self.driver.quit()
                            # self.driver.quit()
                            return 'selenium_success'
                        else:
                            print('检测到最新获取到的cookie为空, 重新登录获取!!')
                    elif 'VPN系统' in self.driver.page_source and 'USB-KEY登录' in self.driver.page_source:
                        print('进入vpn系统登录页面, 休息 10min')
                        time.sleep(600)
                    else:
                        print('没有获取到  文献检索 字眼, 重新来来一次文献检索')
                else:
                    print('通过selenium登录90tsg失败!! 稍等3~5分钟, 重新登录')
                    time.sleep(random.uniform(5, 10))
            except Exception as e:
                print('使用selenium登录出现异常第 {} 次 : {}'.format(i, repr(e)))
                print('通过selenium登录时出现错误!! 稍等1~2分钟, 重新登录')
                time.sleep(random.uniform(60, 120))
            print('开始关闭浏览器!!')
            time.sleep(random.uniform(1,3))
            self.driver.quit()
        pass

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
                    self.driver.quit()
                    return 'selenium_success'
                else:
                    print('通过selenium登录后未出现登录成功!! 稍等3~5分钟, 重新登录')
                    time.sleep(random.uniform(5,10))
            except Exception as e:
                print('使用selenium登录出现异常第 {} 次 : {}'.format(i,repr(e)))
                print('通过selenium登录时出现错误!! 稍等1~2分钟, 重新登录')
                time.sleep(random.uniform(60, 120))
            # self.driver.quit()
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

    def selenium_turn(self,cookies):
        driver = webdriver.Chrome()
        if "expiry" in cookies.keys():
            # dict支持pop的删除函数
            cookies.pop("expiry")
        for name, value in cookies.items():

            print({'name':name,'value':value})
            driver.add_cookie({'name':name,'value':value})
        driver.get('http://www.90tsg.com/e/action/ShowInfo.php?classid=68&id=742')
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
            print('这是data: ',data)
            # self.domain = self.domains[0]
            # print('当前域名为: {}'.format(self.domain))
            if owning_account == '6849_超星3_华中科技大学':
                url = 'http://qikan.chaoxing.a.hknsspj.cn/'
                headers = {
                        # "Host": "qikan.chaoxing.a.fg77.club",
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
                try:
                    res = self.session.post(url,headers=headers,data=data)
                except Exception as e:
                    print('登录发起连接请求时出错: 休息一下, 重新登录',repr(e))
                    time.sleep(5)
                    continue
                res.encoding = 'utf-8'
                if res.status_code == 200 and '来自华中科技大学的朋友' in res.text:
                    print('成功进入 超星期刊 期刊数据库 ,当前是 6849_超星3_华中科技大学 账号')
                    print(self.session.cookies.get_dict())
                    return self.session
                elif '请输入验证码' in res.text:
                    self.cx_code = CxCode(self.session)
                    self.session = self.cx_code.run()
                    print('超星跳转验证码验证成功后, 等待10秒钟,重新登录一次!!')
                    time.sleep(10)
                else:
                    print('当前第 {} 次进入超星期刊数据库失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(5,10))
                    if i > 3:
                        entry_name = '超星期刊3'
                        print('当前通过selenium进入接口为: ',entry_name)
                        print('连续第 {} 次进入 超星期刊数据库 失败, 休息3~5min, 继续登录!'.format(i))
                        time.sleep(random.uniform(180,300))
                        turn_status = self.selenium_login_chaoxing(entry_name)
                        if turn_status == 'selenium_success':
                            print('通过selenium跳转到 超星3 成功 且 已拿到cookie!!')
                            return self.session
            elif owning_account == '6849_超星2_南京财经大学':
                url = 'http://qikan.chaoxing.nc.hknsspj.cn/'
                # url = 'http://qikan.chaoxing.nc.hknsspj.cn/'
                headers = {
                        # "Host": "qikan.chaoxing.nc.fg77.club",
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
                res = self.session.post(url,headers=headers,data=data)
                res.encoding = 'utf-8'
                # print(res.text)
                if res.status_code == 200 and '来自南京财经大学的朋友' in res.text:
                    print('成功进入 超星期刊 期刊数据库 ,当前是 6849_超星2南京财经大学账号')
                    print(self.session.cookies.get_dict())
                    return self.session
                elif '请输入验证码' in res.text:
                    self.cx_code = CxCode(self.session)
                    self.session = self.cx_code.run()
                    print('超星跳转验证码验证成功后, 等待10秒钟,重新登录一次!!')
                    time.sleep(10)
                else:
                    print('当前第 {} 次进入超星期刊数据库失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(5,10))
                    if i > 3:
                        entry_name = '超星期刊2'
                        print('当前通过selenium进入接口为: ',entry_name)
                        print('连续第 {} 次进入 超星期刊数据库 失败, 休息3~5min, 继续登录!'.format(i))
                        time.sleep(random.uniform(180,300))
                        turn_status = self.selenium_login_chaoxing(entry_name)
                        if turn_status == 'selenium_success':
                            print('通过selenium跳转到 超星2 成功 且 已拿到cookie!!')
                            return self.session

            elif owning_account == '6849_超星1_西安交通大学':
                # url = 'http://qikan.chaoxing.j.fg77.club/'
                url = 'http://qikan.chaoxing.j.hknsspj.cn/'

                headers = {
                        # "Host": "qikan.chaoxing.j.fg77.club",
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
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        # "Cookie": "JSESSIONID=E3D36B2D95553F301D1F6FE8C8985654.fx4210; __dxca=161af075-d1e3-4c5f-934e-dc800cfcd49d"
                    }
                res = self.session.post(url,headers=headers,data=data)

                res.encoding = 'utf-8'
                # print(res.text)
                # exit()
                if res.status_code == 200 and '来自西安交通大学的朋友' in res.text:
                    print('成功进入 超星期刊 期刊数据库 ,当前是 6849_超星1西安交通大学账号')
                    print(self.session.cookies.get_dict())
                    return self.session

                elif '请输入验证码' in res.text:
                    self.cx_code = CxCode(self.session)
                    self.session = self.cx_code.run()
                    print('超星跳转验证码验证成功后, 等待10秒钟,重新登录一次!!')
                    time.sleep(10)
                else:
                    print('当前第 {} 次进入超星期刊数据库失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(5,10))
                    if i > 3:
                        entry_name = '超星期刊1'
                        print('当前通过selenium进入接口为: ',entry_name)
                        print('连续第 {} 次进入 超星期刊数据库 失败, 休息3~5min, 继续登录!'.format(i))
                        time.sleep(random.uniform(180,300))
                        turn_status = self.selenium_login_chaoxing(entry_name)
                        if turn_status == 'selenium_success':
                            print('通过selenium跳转到 超星1 成功 且 已拿到cookie!!')
                            return self.session
            elif owning_account == '6849_超星1':
                url = 'http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/'
                headers = {
                        "Host": "nmg.jitui.me",
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
                res = self.session.post(url,headers=headers,data=json.dumps(data))
                if res.status_code == 200 and '超星期刊' in res.text:
                    print('成功进入 超星期刊 期刊数据库 ,当前是 6849_超星期刊1 账号')
                    print(self.session.cookies.get_dict())
                    return self.session

                else:
                    print('当前第 {} 次进入超星期刊数据库失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(5,10))
                    if i > 3:
                        print('连续第 {} 次进入 超星期刊数据库 失败, 休息3~5min, 继续登录!'.format(i))
                        time.sleep(random.uniform(180,300))
                        # turn_status = self.selenium_login_chaoxing()
                        # if turn_status == 'selenium_success':
                        #     print('通过selenium跳转到 超星1 成功 且 已拿到cookie!!')
                        #     return self.session
            elif owning_account == '6849_上海对外经贸大学':
                url = 'https://dldx.jitui.me/http/77726476706e69737468656265737421e1fe4a9d297e6b41680199e29b5a2e/'
                headers = {
                    "Host": "dldx.jitui.me",
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
                # print(res.text)
                print('这是请求状态: ',res.status_code)
                if res.status_code == 200 and '77726476706e69737468656265737421e1fe4a9d297e6b41680199e29b5a2e' in res.text:
                    print('成功进入 维普中文期刊数据库 ,当前是 6849_vip 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入维普中文期刊数据库失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(5,10))
                    if i >= 5:
                        print('连续第 {} 次进入 维普中文期刊数据库 失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
            elif owning_account == '6849_vip':
                url = 'https://dldx.jitui.me/http/77726476706e69737468656265737421e1fe4a9d297e6b41680199e29b5a2e/'
                headers = {
                    "Host": "dldx.jitui.me",
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
                # print(res.text)
                print('这是请求状态: ',res.status_code)
                if res.status_code == 200 and '77726476706e69737468656265737421e1fe4a9d297e6b41680199e29b5a2e' in res.text:
                    print('成功进入 维普中文期刊数据库 ,当前是 6849_vip 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入维普中文期刊数据库失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(5,10))
                    if i >= 5:
                        print('连续第 {} 次进入 维普中文期刊数据库 失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
            elif owning_account == '6849_维普_青岛市图书馆':

                # cookies = self.session.cookies
                # self.selenium_turn(cookies)
                # headers = {
                #     "Host": "www.90tsg.com",
                #     "Connection": "keep-alive",
                #     "Upgrade-Insecure-Requests": "1",
                #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                #     "Referer": "http://www.90tsg.com/e/action/ListInfo/?classid=68",
                #     "Accept-Encoding": "gzip, deflate",
                #     "Accept-Language": "zh-CN,zh;q=0.9"
                # }
                #
                #
                # res = self.session.get('http://www.90tsg.com/e/action/ShowInfo.php?classid=68&id=742',headers=headers)
                # print(res.text)
                headers = {
                    "Host": "qd.jitui.me",
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
                # new_cookie = {'GW1gelwM5YZuT':'5354wQbHX6UWqqqDDUphPxGhtpj0g_ugtp5mPX6zbWXOtKydfFsGpeWuWiQDcvalvy1NCGKjotsoaXxPzTJlkHVqncKrQR3UrZvT.EWlEzlfWMFQ7NLSwfSrtTsekQHtZ2N.WBx8ClNwb8eP6lZ93_2tP9oDsLfYaWkaG7HxoT9UeEgrAyyuejahNlFk4iFuGNVTynKcBAxlakGGQQfzXTpFVUQoxAqcDitp2BoCuqFhMSKus73h2iJp7L0fVbRFmZ'}
                # self.session.cookies.update(new_cookie)
                res = self.session.post('http://qd.jitui.me/interlibSSO/main/GotoSys.jsp?sysid=46', data=json.dumps(data),headers=headers)
                # print(res.text)
                # print('这是第二次请求前的cookies: ',self.session.cookies.get_dict())
                # print('这是res.url: ',res.url)
                url = res.url
                headers = {
                        # "Host": "qikan.cqvip.com",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "Referer": url,
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        # "Cookie": "GW1gelwM5YZuS=5xiLDU0FVTbFMXm6QPOLcld_hmElGCrsTPklDEYfsJgBPmkJ4cgB7XXdJ6jZx3rqZLTNxhRvqOtxiiPMzESQkKq; GW1gelwM5YZuT=535CooCHzfnqqqqDDYeIVwAmEn6yUVQ5f1X_g58FiDyRKnDwx5sU0DZ9DXFgIPUCBBfO1V3Ugo4eh538jWTL63i4eOq6rGVeWh6sE0lIQiyZJKptWV5.AMjArgmh4_9JexK17llz85fUWg.8EjWN1stlhdp0Yqi8aZ7aKLHW91yPw4BoBtgYw_V8V03g.EAALUf5nG3OFXyQyKyv8IdfwdLwsUWixlu.9OK_FSvqg8qT.WckbRSW9d0gdcEDRYGihWgd2a5ldpTAQodU0At87yI"
                    }
                res = self.session.get(url,headers=headers)
                print(self.session.cookies.get_dict())

                print(res.status_code)
                print(res.text)
                exit()
            elif owning_account == '6849_中国生物_':
                headers = {
                        # "Host": "www.sinomed.a.hknsspj.cn",
                        "Connection": "keep-alive",
                        "Content-Length": "46",
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": "http://www.90tsg.com",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                res = self.session.post('http://www.sinomed.a.hknsspj.cn/index.jsp',headers=headers,data=data)
                # print(res.text)
                if res.status_code == 200 and '中国生物医学文献服务系统' in res.text:
                    print('成功进入中国生物医学文献服务系统,当前是 6849_中国生物_ 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入中国生物医学文献服务系统失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(10,20))
                    if 'VPN系统' in res.text and 'USB-KEY登录' in res.text:
                        print('登录中国生物医学文献系统时, 跳转到了Vpn登录页面, 休息10~20min 重新登录!!')
                        time.sleep(random.uniform(600,1200))
                    if i >= 5:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
                        # entry_name = '中国生物医学2'
                        # res_status = self.selenium_login_chinasw(entry_name)
                        # if res_status == 'selenium_success':
                        #     print('成功进入 {} '.format(entry_name))
                        #     return self.session
                    # self.domains.reverse()
            elif owning_account == '6849_中国生物_东单校园网':
                headers = {
                        "Host": "www-sinomed-ac-cn.beijingxiehe.tsg211.com",
                        "Connection": "keep-alive",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                res = self.session.get('http://www-sinomed-ac-cn.beijingxiehe.tsg211.com/zh/',headers=headers)
                # print(res.text)
                if res.status_code == 200 and '中国生物医学文献服务系统' in res.text:
                    print('成功进入中国生物医学文献服务系统,当前是 6849_中国生物_东单校园网 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入中国生物医学文献服务系统失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(10,20))
                    if 'VPN系统' in res.text and 'USB-KEY登录' in res.text:
                        print('登录中国生物医学文献系统时, 跳转到了Vpn登录页面, 休息10~20min 重新登录!!')
                        time.sleep(random.uniform(600,1200))
                    if i >= 5:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
                        # entry_name = '中国生物医学2'
                        # res_status = self.selenium_login_chinasw(entry_name)
                        # if res_status == 'selenium_success':
                        #     print('成功进入 {} '.format(entry_name))
                        #     return self.session
                    # self.domains.reverse()
            elif owning_account == '6849_南京医科大学':
                headers = {
                        "Host": "www-sinomed-ac-cn.njmu.hknsspj.cn",
                        "Connection": "keep-alive",
                        "Content-Length": "46",
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": "http://www.90tsg.com",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                res = self.session.post('http://www-sinomed-ac-cn.njmu.hknsspj.cn/index.jsp', data=json.dumps(data),headers=headers)
                # print(res.text)
                if res.status_code == 200 and '中国生物医学文献服务系统' in res.text:
                    print('成功进入中国生物医学文献服务系统,当前是 6849_南京医科大学 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入中国生物医学文献服务系统失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(10,20))
                    if 'VPN系统' in res.text and 'USB-KEY登录' in res.text:
                        print('登录中国生物医学文献系统时, 跳转到了Vpn登录页面, 休息10~20min 重新登录!!')
                        time.sleep(random.uniform(600,1200))
                    if i >= 5:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息10~15min, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
                        # entry_name = '中国生物医学2'
                        # res_status = self.selenium_login_chinasw(entry_name)
                        # if res_status == 'selenium_success':
                        #     print('成功进入 {} '.format(entry_name))
                        #     return self.session
                    # self.domains.reverse()
            #     华中科技大学同济医学院
            elif owning_account == '6849_复旦大学':
                # self.domains = ['www-sinomed-ac-cn.njmu.jitui.me','www.sinomed.a.fg77.club']

                headers = {
                        # "Host": "www.sinomed.g.fg77.club",
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
                res = self.session.post('http://www.sinomed.g.fg77.club/', data=json.dumps(data),headers=headers)
                # print(res.text)
                if res.status_code == 200 and '中国生物医学文献服务系统' in res.text:
                    print('成功进入中国生物医学文献服务系统,当前是 6849_华中科技大学同济医学院 账号')
                    return self.session
                else:
                    print('当前第 {} 次进入中国生物医学文献服务系统失败, 休息一下, 继续登录!'.format(i))
                    time.sleep(random.uniform(2, 5))
                    if 'VPN系统' in res.text and 'USB-KEY登录' in res.text:
                        print('登录中国生物医学文献系统时, 跳转到了Vpn登录页面, 休息10~20min 重新登录!!')
                        time.sleep(random.uniform(600,1200))
                    if i >= 5:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息一会儿, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
                        # entry_name = '中国生物医学2'
                        # res_status = self.selenium_login_chinasw(entry_name)
                        # if res_status == 'selenium_success':
                        #     print('成功进入 {} '.format(entry_name))
                        #     return self.session
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
                    if 'VPN系统' in res.text and 'USB-KEY登录' in res.text:
                        print('登录中国生物医学文献系统时, 跳转到了Vpn登录页面, 休息10~20min 重新登录!!')
                        time.sleep(random.uniform(600,1200))
                    time.sleep(random.uniform(2, 5))
                    if i >= 2:
                        print('连续第 {} 次进入中国生物医学文献服务系统失败, 休息一会儿, 继续登录!'.format(i))
                        time.sleep(random.uniform(600,900))
                        # entry_name = '中国生物医学2'
                        # res_status = self.selenium_login_chinasw(entry_name)
                        # if res_status == 'selenium_success':
                        #     print('成功进入 {} '.format(entry_name))
                        #     return self.session
            elif owning_account == '6849_杭州师范大学':
                headers = {
                        "Host": "hzsf66nkjgdrngkedrgnkdrfjgnkd.98tsg.com",
                        "Connection": "keep-alive",
                        "Content-Length": "44",
                        "Accept": "application/json, text/plain, */*",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                        "Content-Type": "application/json",
                        "Origin": "http://hzsf66nkjgdrngkedrgnkdrfjgnkd.98tsg.com",
                        "Referer": "http://hzsf66nkjgdrngkedrgnkdrfjgnkd.98tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                data_login = {"condition": {"loginName": "", "password": ""}}
                res = self.session.post('http://hzsf66nkjgdrngkedrgnkdrfjgnkd.98tsg.com/getCore/pcLogin', data=json.dumps(data_login),
                                        headers=headers)
                print(res.text)
                if res.status_code == 200 and res.json()['success'] == True:
                    print('成功进入中华医学网,当前是 6849_杭州师范大学 账号')
                    return self.session,res.json()
                else:
                    print('当前第 {} 次登录中华医学网失败, 继续登录!'.format(i))
                    time.sleep(2)

            elif owning_account == '6849_医学会_福建医科大学':
                first_url = 'http://yiigle-meddata-com-cn.fjmu.hknsspj.cn/'
                first_headers = {
                        # "Host": "yiigle-meddata-com-cn.fjmu.hknsspj.cn",
                        "Connection": "keep-alive",
                        "Content-Length": "46",
                        "Cache-Control": "max-age=0",
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": "http://www.90tsg.com",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Referer": "http://www.90tsg.com/",
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9"
                    }
                headers = {
                            "Host": "yiigle-meddata-com-cn.fjmu.hknsspj.cn",
                            "Connection": "keep-alive",
                            "Content-Length": "44",
                            "Accept": "application/json, text/plain, */*",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                            "Content-Type": "application/json",
                            "Origin": "http://yiigle-meddata-com-cn.fjmu.hknsspj.cn",
                            "Referer": "http://yiigle-meddata-com-cn.fjmu.hknsspj.cn/",
                            "Accept-Encoding": "gzip, deflate",
                            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
                        }
                data_login = {"condition": {"loginName": "", "password": ""}}
                try:
                    res = self.session.post(first_url,headers=first_headers,json=data,timeout=(20,30))
                    print(res.text)
                    # exit()

                    res = self.session.post('http://yiigle-meddata-com-cn.fjmu.hknsspj.cn/getCore/pcLogin', data=json.dumps(data_login),
                                            headers=headers)
                    print(res.text)
                    if res.status_code == 200 and res.json()['success'] == True:
                        print('成功进入中华医学网,当前是 6849_福建医科大学 账号')
                        return self.session,res.json()
                    else:
                        print('当前第 {} 次登录中华医学网失败, 继续登录!'.format(i))
                        time.sleep(2)
                except Exception as e:
                    print('登录程序进入中华医学网出现问题, 账号为: 6849_福建医科大学, 休息一下, 重新发起请求!!')
                    time.sleep(random.uniform(5,10))

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

# login = LoginTrun('6849_超星1_西安交通大学')
# login.login_page_turn('6849_超星1_西安交通大学')
# login.selenium_login_chaoxing('超星期刊2')
# login = LoginTrun('6849_南京医科大学')
# # # login.login_page_turn('6849_超星3_华中科技大学')
# login.selenium_login_chinasw('中国生物医学2')