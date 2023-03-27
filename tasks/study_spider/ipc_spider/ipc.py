import json
import re

import execjs
import requests


class Ipc():

    def __init__(self):

        self.session = requests.Session()

    def get_enkey(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        enkey_url = 'http://icp.chinaz.com/record/baidu.com'
        res = self.session.get(enkey_url, headers=headers)
        if re.findall("var enkey = '(.*?)';", res.text):
            enkey = re.findall("var enkey = '(.*?)';", res.text)[0]
            print('这是 get_enkey 得到的enkey',enkey)
            return enkey
        else:
            print('enkey匹配不到!!')

    def get_mid_key(self, word):

        ctx = execjs.compile(open('ipc1.js', 'r', encoding='utf-8').read())
        mid_key = ctx.call('generateWordKey', word)
        print('mid_key为: {}'.format(mid_key))
        return mid_key

    def get_token(self, mid_key, enkey):
        # key = generateWordKey('baidu.com');
        # console.log(key);
        #
        # data = generateHostMD5Key('383,481,480,488,483,500,429,482,494,492','NOI1PtcXVP1l4DcCx6GYyqP~lS4m5QdcI849EWpEUDGScOcK2fIZ6Zbig2s8TGi0');
        # console.log(data);
        ctx = execjs.compile(open('ipc1.js', 'r', encoding='utf-8').read())
        token = ctx.call('generateHostMD5Key', mid_key, enkey)
        print('token值为: {}'.format(token))
        return token

    def get_randomnum(self, mid_key):

        ctx = execjs.compile(open('ipc2.js', 'r', encoding='utf-8').read())
        randomnum = ctx.call('getRandomNum', mid_key)
        print('这是randomnum: {}'.format(randomnum))
        return randomnum

    def get_data(self, word, enkey, randomNum, token):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'icp.chinaz.com',
            'X-Requested-With': 'XMLHttpRequest',
            # 'Cookie': 'Hm_lvt_ca96c3507ee04e182fb6d097cb2a1a4c=1662458517,1662510321; .AspNetCore.Session=CfDJ8CdB96UITKRDua5BVQevwLeuQj3x0UuZ0Dhj9GlSGdNFhQ7gOAIvLBxReY%2BUOLLordxghZiI1kpwLdHpRO683%2B7npKVZES3gwox5NLFB43jGfZjTlkZhQ8vBhADDuef717kUf6DtwWY9cpigpoAu9onvoDQJeLDlHwp7hI0H1D0y; .AspNetCore.Antiforgery.ZLR_yHWNBdY=CfDJ8CdB96UITKRDua5BVQevwLcxPL29AizqB_T9IAJ5e9ZZQQ3LGh4frx8xgerQvKHzMaU9mGVy4Y9sMdotXhPADDKn-SYeNd0kXWA-vV5A9DZwILdD63AiZytYnPbwm7UXzzCYDMhSkpkF8fe4m1Po29E; .AspNetCore.Antiforgery.2htDGZ9yTBg=CfDJ8NApB498u2FKm9ciPl1xfdqaMubzyx4IUJzGuaKpxbcpn5Fo3xmKjBLB3R_nWs0CXr4ZzNlJCEeQWuHn5wH25pvkJm-w3J30yU3tYwNMBG9f8pwzJtK-UZMFjcld0ambUlgjHxvnwTlSkLvrgcIX280; Hm_lpvt_ca96c3507ee04e182fb6d097cb2a1a4c=1662521568',
            # 'Content-Length': '159'
        }
        url = 'http://icp.chinaz.com/Record/PageData'
        data = {
            'pageNo': 1,
            'pageSize': 20,
            'kw': word,
            'enKey': enkey,
            'randomNum': randomNum,
            'token': token
        }
        # data = {
        #     'pageNo': 1,
        #     'pageSize': 20,
        #     'kw': 'baidu.com',
        #     'enKey': 'NOI1PtcXVP1l4DcCx6GYyqP~lS4m5QdcI849EWpEUDHCvNP2ucNjkYGkJotOZZ|0',
        #     'randomNum': '781',
        #     'token': '0ce486a0a18ae29b2672e9f36601b5b5'
        # }
        #
        res = self.session.post(url, data=data, headers=headers)
        print(res.text)


    def run(self):
        word = input('请输入要查询的关键字: ')
        enkey = self.get_enkey()
        mid_key = self.get_mid_key(word)
        token = self.get_token(mid_key, enkey)
        randomNum = self.get_randomnum(mid_key)
        self.get_data(word,enkey, randomNum, token)
        # self.get_data(1,2,3,4)

if __name__ == '__main__':
    ipc = Ipc()
    ipc.run()


# 总结:
#
#   1 formdata数据不能再使用json.dumps 进行编码请求
# 思路:
#     1 fiddler模拟请求
#         整体模拟过程中, 先使用fiddler模拟,查看能否获取到, 并且查看哪些参数是变量, 哪些是定量, 对于变量, 我们需要锁定到变量的获取过程与位置
#     2 断点调试,获取逻辑与具体的传参与值返回过程
#         混淆, 首先需要用js_tools工具进行反混淆得到近似源码, 扣出目标数据相关js代码, 接下来就是对近似源码进行目标源码逻辑的阅读, 这个过程中锁定参数与返回数据, 从浏览器查看具体的参数是谁, 调用时怎样的
#     3 本地调试js
#         缺啥补啥, 最终得到结果
#     4 模拟js逻辑, 使用python执行
#         pyexecjs模块执行获取到最终结果数据
#   2 整体模拟过程中, 先使用fiddler模拟,查看能否获取到, 并且查看哪些参数是变量, 哪些是定量, 对于变量, 我们需要锁定到变量的获取过程与位置, 在断点调试的过程中, 遇到混淆, 首先需要用js_tools工具进行反混淆得到近似源码, 接下来就是对近似源码进行目标源码逻辑的阅读, 这个过程中锁定参数与返回数据, 从浏览器查看具体的参数是谁, 调用时怎样的, 接下来开始扣js, 之后在本地调试, 缺啥补啥, 最终得到结果, 通过python execjs模块执行获取到最终结果数据