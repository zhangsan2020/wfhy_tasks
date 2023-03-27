import random
import time

import requests
headers = {
            "Host": "hnztbkhd.fgw.henan.gov.cn",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page=7",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }


for i in range(1,5):
    url = 'http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page={}'.format(i)
    res = requests.get(url,headers=headers)
    print(res.text)
    with open('new_{}.html'.format(i),'w',encoding='utf-8') as f:
        f.write(res.text)
        f.close()
# session = requests.Session()
# headers = {
#     "Host": "hnztbkhd.fgw.henan.gov.cn",
#     "Connection": "keep-alive",
#     "Upgrade-Insecure-Requests": "1",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#     "Referer": "http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page=8",
#     "Accept-Encoding": "gzip, deflate",
#     "Accept-Language": "zh-CN,zh;q=0.9"
# }
# time_1 = str(int(time.time()))
# for i in range(2,5):
#     headers = {
#         "Host": "hnztbkhd.fgw.henan.gov.cn",
#         "Connection": "keep-alive",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "Referer": "http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page={}".format(i-1),
#         "Accept-Encoding": "gzip, deflate",
#         "Accept-Language": "zh-CN,zh;q=0.9"
#     }
#     print('这是headers: ',headers)
#     print('当前是第 {} 页'.format(i))
#     # print(repr(headers))
#     res = session.get(url,headers=headers)
#     # print(res.text)
#     with open('aa_{}.html'.format(i),'w',encoding='utf-8') as f:
#         f.write(res.text)
#         f.close()
# #     headers_js = {
# #     "Host": "hm.baidu.com",
# #     "Connection": "keep-alive",
# #     "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
# #     "sec-ch-ua-mobile": "?0",
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
# #     "sec-ch-ua-platform": "\"Windows\"",
# #     "Accept": "*/*",
# #     "Sec-Fetch-Site": "cross-site",
# #     "Sec-Fetch-Mode": "no-cors",
# #     "Sec-Fetch-Dest": "script",
# #     "Referer": "http://hnztbkhd.fgw.henan.gov.cn/",
# #     "Accept-Encoding": "gzip, deflate, br",
# #     "Accept-Language": "zh-CN,zh;q=0.9",
# #     "Cookie": "HMACCOUNT_BFESS=8045D929CC5C12CF",
# #     "If-None-Match": "ecbb54191f38669462c875388ca61ece"
# # }
# #     res = session.get('https://hm.baidu.com/hm.js?da6ebc493961b944c4bf10a22517a198',headers=headers_js)
# #     # print(res.text)
#     time_2 = str(int(time.time()))
#     cookies = {
#         'Hm_lvt_da6ebc493961b944c4bf10a22517a198':time_1,
#         'Hm_lpvt_da6ebc493961b944c4bf10a22517a198':time_2
#     }
#     # session.cookies.get_dict()
#     session.cookies.update(cookies)
#     # session.cookies.set_cookie()
#     print(session.cookies)
#     time.sleep(random.uniform(3,5))
#
#
#     url1 = 'https://hm.baidu.com/hm.js?da6ebc493961b944c4bf10a22517a198'
#