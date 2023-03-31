# import random
# import time
# 
# import requests
# headers = {
#             "Host": "hnztbkhd.fgw.henan.gov.cn",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#             "Referer": "http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page=7",
#             "Accept-Encoding": "gzip, deflate",
#             "Accept-Language": "zh-CN,zh;q=0.9"
#         }
# 
# 
# for i in range(1,5):
#     url = 'http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page={}'.format(i)
#     res = requests.get(url,headers=headers)
#     print(res.text)
#     with open('new_{}.html'.format(i),'w',encoding='utf-8') as f:
#         f.write(res.text)
#         f.close()
# # session = requests.Session()
# # headers = {
# #     "Host": "hnztbkhd.fgw.henan.gov.cn",
# #     "Connection": "keep-alive",
# #     "Upgrade-Insecure-Requests": "1",
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
# #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
# #     "Referer": "http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page=8",
# #     "Accept-Encoding": "gzip, deflate",
# #     "Accept-Language": "zh-CN,zh;q=0.9"
# # }
# # time_1 = str(int(time.time()))
# # for i in range(2,5):
# #     headers = {
# #         "Host": "hnztbkhd.fgw.henan.gov.cn",
# #         "Connection": "keep-alive",
# #         "Upgrade-Insecure-Requests": "1",
# #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
# #         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
# #         "Referer": "http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page={}".format(i-1),
# #         "Accept-Encoding": "gzip, deflate",
# #         "Accept-Language": "zh-CN,zh;q=0.9"
# #     }
# #     print('这是headers: ',headers)
# #     print('当前是第 {} 页'.format(i))
# #     # print(repr(headers))
# #     res = session.get(url,headers=headers)
# #     # print(res.text)
# #     with open('aa_{}.html'.format(i),'w',encoding='utf-8') as f:
# #         f.write(res.text)
# #         f.close()
# # #     headers_js = {
# # #     "Host": "hm.baidu.com",
# # #     "Connection": "keep-alive",
# # #     "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
# # #     "sec-ch-ua-mobile": "?0",
# # #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
# # #     "sec-ch-ua-platform": "\"Windows\"",
# # #     "Accept": "*/*",
# # #     "Sec-Fetch-Site": "cross-site",
# # #     "Sec-Fetch-Mode": "no-cors",
# # #     "Sec-Fetch-Dest": "script",
# # #     "Referer": "http://hnztbkhd.fgw.henan.gov.cn/",
# # #     "Accept-Encoding": "gzip, deflate, br",
# # #     "Accept-Language": "zh-CN,zh;q=0.9",
# # #     "Cookie": "HMACCOUNT_BFESS=8045D929CC5C12CF",
# # #     "If-None-Match": "ecbb54191f38669462c875388ca61ece"
# # # }
# # #     res = session.get('https://hm.baidu.com/hm.js?da6ebc493961b944c4bf10a22517a198',headers=headers_js)
# # #     # print(res.text)
# #     time_2 = str(int(time.time()))
# #     cookies = {
# #         'Hm_lvt_da6ebc493961b944c4bf10a22517a198':time_1,
# #         'Hm_lpvt_da6ebc493961b944c4bf10a22517a198':time_2
# #     }
# #     # session.cookies.get_dict()
# #     session.cookies.update(cookies)
# #     # session.cookies.set_cookie()
# #     print(session.cookies)
# #     time.sleep(random.uniform(3,5))
# #
# #
# #     url1 = 'https://hm.baidu.com/hm.js?da6ebc493961b944c4bf10a22517a198'
# #
import re
from urllib.parse import urljoin

from lxml import etree

domain = 'vp.vip.tsg211.com'
with open('维普list.html','r',encoding='utf-8') as f:
    html = etree.HTML(f.read())
    f.close()
dls = html.xpath('//div[@id="remark"]/dl')

for dl in dls:
    item = {}
    down_flag = dl.xpath('./dd[@class="source"]//a/text()')
    print(down_flag)
    if '下载PDF' in down_flag:
        name = dl.xpath('./dt[1]/a/text()')[0].strip()
        articleid = dl.xpath('./dt[1]/a/@articleid')[0].strip()
        item['file_name'] = '{}_{}.pdf'.format(name, articleid)
        print('文件名为: {}'.format(item['file_name']))
        # filter_status = redis_wp.set_item('wp_file_name', item['file_name'])
        # if filter_status:
        # http://vp.vip.tsg211.com/Qikan/Article/Detail?id=7108873433
        item['detail_url'] = urljoin('http://' + domain, dl.xpath('./dt[1]/a/@href')[0].strip())
        refer_num = dl.xpath('./dt[1]/span[@class="cited"]/a/text()')
        if refer_num:
            item['reference_count'] = refer_num[0]
        else:
            item['reference_count'] = 0
        # './/span[@class="author"][1]//span[1:]/a/@title'
        author_datas = dl.xpath('.//span[@class="author"][1]/span[position()>1]')

        # print(';'.join([author_data.xpath('./a/@title')[0] for author_data in author_datas if len(author_data.xpath('./a/@title'))>0]))
        # print(author_data)
        if author_datas:
            item['authors'] = ';'.join([author_data.xpath('./a/@title')[0] for author_data in author_datas if len(author_data.xpath('./a/@title'))>0])
        else:
            item['authors'] = ''
        origin_from_data = dl.xpath('.//span[@class="from"][1]/a/@title')
        if origin_from_data:
            item['origin_from'] = dl.xpath('.//span[@class="from"][1]/a/@title')[0].strip()
        else:
            item['origin_from'] = ''
        item['article_keyword_data'] = ';'.join(dl.xpath('.//span[@class="subject"][1]/span/a/@title'))
        pdf_params_tag = etree.tostring(dl.xpath('.//div[@class="article-source"][1]')[0]).decode().strip()
        pdf_params_data = re.findall("showdown\('(\d+)','(.*?)'\)",pdf_params_tag)
        if pdf_params_data and pdf_params_data[0]:
            # id=7108994675&info=pITdbrEQxhHwTDkOkK08lY0hIE9wD0ZIBl6bAE7pscdy4fkASkSJIQ%3D%3D&ts=1680143657797
            pdf_params = 'id={}&info={}'.format(pdf_params_data[0][0],pdf_params_data[0][1])
        print(item)
        print(pdf_params)