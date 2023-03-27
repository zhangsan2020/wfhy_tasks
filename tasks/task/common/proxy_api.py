#coding=utf-8
import requests
import os
os.environ['NO_PROXY'] = 'baidu.com'

#请求地址
targetUrl = "https://www.baidu.com"

#代理服务器
proxyHost = "27.158.35.198"
proxyPort = "16248"

# proxyMeta = "http://%(host)s:%(port)s" % {
#
#     "host" : proxyHost,
#     "port" : proxyPort,
# }
#         '115.208.82.191:20516'
        # 115.209.224.188:19139
        # 122.241.54.200:22551
        # 114.219.129.192:18037
        # 27.158.35.198:16248'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
# proxy_ip = '115.209.224.188:19139'
# proxys = {'http':proxy_url, 'https':proxy_url}

# proxies = {
#     "http": "http://%(proxy)s/" % {"proxy": proxy_ip},
#     "https": "http://%(proxy)s/" % {"proxy": proxy_ip}
# }
# resp = requests.get(targetUrl, proxies=proxies, headers=headers)
# print(resp.status_code)
# print(resp.text)



# # # 用户名密码认证(私密代理/独享代理)
# username = "15210559392"
# password = "jiamianwuke2018"
# import requests
#
# # 提取代理API接口，获取1个代理IP
# api_url = "https://dps.kdlapi.com/api/getdps/?secret_id=opftq08u1cf8b25x3n2k&num=10&signature=o85b65evs62p6ri28farr108gi&pt=1&sep=1"
# # 获取API接口返回的代理IP
# proxy_ip = requests.get(api_url).text
# print(proxy_ip)
# # proxy_ip = '117.68.193.187:22463'
# proxies = {
#     "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
#     "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
# }
# # # 要访问的目标网页
# target_url = "https://dev.kdlapi.com/testproxy"
# # 使用代理IP发送请求
# response = requests.get(target_url, proxies=proxies)
# print(response.status_code)
# # 获取页面内容
# if response.status_code == 200:
#     print(response.text)


"""
使用requests请求代理服务器
请求http和https网页均适用
"""

import requests



def get_ip():
    username = "1029025432"
    password = "halkvqpf"


    # 提取代理API接口，获取1个代理IP
    api_url = "https://dps.kdlapi.com/api/getdps/?secret_id=opftq08u1cf8b25x3n2k&num=1&signature=oi3jvnqbi0s9mndcx68uvtpiv6&pt=1&sep=1"

    # 获取API接口返回的代理IP
    proxy_ip = requests.get(api_url).text
    print(proxy_ip)

    # 用户名密码认证(私密代理/独享代理)
    # username = "username"
    # password = "password"
    proxies = {
        "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip},
        "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": proxy_ip}
    }

    # proxy_ip = '122.241.53.53:15390'
    # proxy_ip = '122.241.53.53'
    # 白名单方式（需提前设置白名单）
    # proxies = {
    #     "http": "http://%(proxy)s/" % {"proxy": proxy_ip},
    #     "https": "http://%(proxy)s/" % {"proxy": proxy_ip}
    # }
    # 要访问的目标网页
    target_url = "https://dev.kdlapi.com/testproxy"
    target_url = 'http://www.baidu.com'

    # 使用代理IP发送请求
    response = requests.get(target_url, proxies=proxies)

    # 获取页面内容
    if response.status_code == 200:
        print(response.text)
        return proxies
get_ip()