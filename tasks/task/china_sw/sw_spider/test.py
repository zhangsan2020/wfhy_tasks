#
# import re
#
# # phone = '28032013000100009.'
# # phone = '28032013000100009'
# # phone = '130001000094651 作者'
# phone = '130001000099 作者'
# # phone = '0003319719900734.'
# print(re.findall('(1[345678]\d{9})[^.\d]', phone))


# from urllib.parse import quote
# KEYWORD = 'ipad'
# url = 'https://s.taobao.com/search?q=' + quote(KEYWORD)
# print(url)
# # 运行结果：https://s.taobao.com/search?q=ipad
# KEYWORD = '病'
# url = 'http://www.yiigle.yz.jd314.vip/Paper/Search?type=&q={}&searchType=pt'.format(quote(KEYWORD))
# print(url)
# 运行结果：https://s.taobao.com/search?q=3346778
# http://www.yiigle.yz.jd314.vip/Paper/Search?type=&q=%E7%97%85&searchType=pt
# http://www.yiigle.yz.jd314.vip/Paper/Search?type=&q=%E7%97%85&searchType=pt
import random
import re
# from datetime import datetime
# data = '2022-06-30T12:19:01.000+00:00'
# print(data.split('T')[0])
# date_str = data.split('T')[0]
# str_date = datetime.strptime(date_str,'%Y-%m-%d').date()
# print(str_date.strftime('%Y年%m月%d日'))
# a = (1,2)
# c,d = a
# print(c)
# print(d)
# elif owning_account == '6849_南方科技大学':
# headers = {
#     "Host": "zdcsxylsrijgoieurjhgfo.98tsg.com",
#     "Connection": "keep-alive",
#     "Content-Length": "44",
#     "Accept": "application/json, text/plain, */*",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
#     "Content-Type": "application/json",
#     "Origin": "http://zdcsxylsrijgoieurjhgfo.98tsg.com",
#     "Referer": "http://zdcsxylsrijgoieurjhgfo.98tsg.com/",
#     "Accept-Encoding": "gzip, deflate",
#     "Accept-Language": "zh-CN,zh;q=0.9"
# }
# data_login = {"condition": {"loginName": "", "password": ""}}
# res = self.session.post('http://zdcsxylsrijgoieurjhgfo.98tsg.com/getCore/pcLogin',
#                         data=json.dumps(data_login),
#                         headers=headers)
# print(res.text)
# if res.status_code == 200 and res.json()['success'] == True:
#     print('成功进入中华医学网,当前是 6849_南方科技大学 账号')
#     return self.session, res.json()
# else:
#     print('当前第 {} 次登录中华医学网失败, 继续登录!'.format(i))
#     time.sleep(2)
# import time
#
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
#
# chrome_options = Options()
# # 把Chrome设置成无界面模式
# # chrome_options.headless = True
# driver = webdriver.Chrome(options=chrome_options)
# print(driver.get_cookies())
#
# session = requests.Session()
# def selenium_login():
#
#     url = 'http://www.90tsg.com/e/member/login/'
#     for i in range(10):
#         print('开始使用selenium进行第 {} 次登录'.format(i))
#         try:
#             driver.get(url)
#             time.sleep(3)
#             driver.find_element(By.ID,'username').send_keys('00966849')
#             driver.find_element(By.ID,'password').send_keys('971152')
#             driver.find_element(By.NAME,'Submit').click()
#             print('第 {} 登录中 点击提交完成!! 请等待10秒, 查看登录状态!!'.format(i))
#             time.sleep(10)
#             if '您身边的数字图书馆' in driver.page_source:
#                 print('90tsg 登录成功!!')
#                 print(driver.get_cookies())
#                 cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
#                 print(cookies)
#                 session.cookies.update(cookies)
#                 print('这是session中的cookies',session.cookies)
#                 driver.close()
#
#                 break
#             else:
#                 print('通过selenium登录后未出现登录成功!! 稍等3~5分钟, 重新登录')
#
#         except:
#             print('通过selenium登录时出现错误!! 稍等3~5分钟, 重新登录')
#         print('通过selenium登录失败第 {} 次'.format(i))
#         time.sleep(random.uniform(180, 300))
#
#
# selenium_login()
# "心理护理干预对经动脉化疗栓塞术序贯化疗治疗<font color='red'>胃癌</font>伴肝转移效果的影响"
# # "心理护理干预对经动脉化疗栓塞术序贯化疗治疗<font color="red">胃癌</font>伴肝转移效果的影响</h5>"
# data = "心理护理干预对经动脉化疗栓塞术序贯化疗治疗fontcolorred胃癌font伴肝转移效果的影响"
# print(data.replace('fontcolorred', '').replace('font',''))
# '心理护理干预对经动脉化疗栓塞术序贯化疗治疗胃癌伴肝转移效果的影响'
# import os
# print(os.popen('tasklist | findstr *.exe').readlines())
import os, re


def start_python_module(module_name):
    # 查看所有運行的python程序
    python_full = os.popen("wmic process where name='python39.exe' list full").readlines()
    # print(python_full)
    if python_full:
        all_python = ''.join([commandline for commandline in python_full if 'CommandLine' in commandline]).replace('\n','')
        print(all_python)
        # for sw_python in all_python:
        if module_name in all_python:
            print('{} 程序正在运行中, 不做处理!'.format(module_name))
        else:
            cmdline = "C:/Users/hello/AppData/Local/Programs/Python/Python39/python39.exe F:/wanfang_tasks/tasks/%s" % module_name
            print(cmdline)
            os.system(cmdline)
            print("{} 程序啟動完成".format(module_name))

if __name__ == '__main__':
    # python程序名
    module_name = 'run_sw_fudandx.py'
    start_python_module(module_name)