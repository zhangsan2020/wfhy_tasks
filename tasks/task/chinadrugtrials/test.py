# # import requests
# # dir_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.prosearch.dhtml'
# # session = requests.Session()
# # headers = {
# #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
# #     'Referer': 'http://www.chinadrugtrials.org.cn/clinicaltrials.prosearch.dhtml'
# # }
# # r = session.get(dir_url,headers=headers)
# # # print(r.text)
# # print(dict(r.cookies.items()))
# # first_cookies = dict(r.cookies.items())
# # # for k,v in r
# # res = session.get(dir_url,headers=headers)
# # # print(res.cookies.items())
# # seconde_cookies = dict(res.cookies.items())
# # print(seconde_cookies)
# # #
# # all_cookies = seconde_cookies.update(first_cookies)
# # print(seconde_cookies)
# # session.cookies.update(seconde_cookies)
# # print(session.cookies)
# #
# # list_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml'
# # data = {
# #     "id":"",
# #     "ckm_index":"",
# #     "sort":"desc",
# #     "sort2":"",
# #     "rule":"CTR",
# #     "secondLevel":0,
# #     "currentpage":2,
# #     "keywords":"动脉粥样硬化"
# # }
# # headers_list = {
# #     "Content-Type": "application/x-www-form-urlencoded",
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
# # }
# #
# # r = session.post(list_url,data=data,headers=headers_list)
# # print(r.text)
# #
# # detail_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlistdetail.dhtml'
# # data = {
# #     "id": "d389034c660b435ab7aa336f598f1345",
# #     "ckm_index": "2",
# #     "sort": "desc",
# #     # sort2:
# #     # "rule": "CTR",
# #     # secondLevel: 0
# #     # currentpage: 1
# #     "keywords": "动脉粥样硬化"
# #     # reg_no:
# #     # indication:
# #     # case_no:
# #     # drugs_name:
# #     # drugs_type:
# #     # appliers:
# #     # communities:
# #     # researchers:
# #     # agencies:
# #     # state: "
# # }
# # headers_detail = {
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
# #     "Content-Type": "application/x-www-form-urlencoded"
# # }
# #
# # res = session.post(detail_url,data=data,headers=headers_list)
# # print(res.text)
# import re
#
# from lxml import etree
#
# with open('./test_list.html','r',encoding='utf-8') as f:
#     html = f.read()
# data = etree.HTML(html)
# # tds = data.xpath('//table[@class="searchDetailTable marginBtm10"]//td')
# # name = tds[0].xpath('./text()')[0]
# # position = tds[2].xpath('./text()')[0]
# # phone = tds[3].xpath('./text()')[0]
# # email = tds[4].xpath('./text()')[0]
# # print(name,position,phone,email)
# # phone = ''
# # print(re.match('(\d+){11}', phone))
# # if re.match('(\d+){11}', phone):
# #     pass
#
# first_register_card = data.xpath('//tr[@class="Tab_title"][1]/following-sibling::tr[1]/td[2]/a/text()')[0].strip()
# print(first_register_card)
# # import requests
# #
# # session = requests.Session()
# # url = 'http://www.ccgp-ningxia.gov.cn//site/InteractionQuestion_findVNoticeNew.do'
# # headers = {
# #     "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
# #     "Host": "www.ccgp-ningxia.gov.cn",
# #     "Origin": "http://www.ccgp-ningxia.gov.cn",
# #     "Referer": "http://www.ccgp-ningxia.gov.cn/public/NXGPPNEW/dynamic/contents/CGGG/index.jsp?cid=312&sid=1",
# #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
# # }
# #
# # data = {
# #     "type": "ALL",
# #     "page": 1,
# #     "tab": "QBJ",
# #     "authCode": "",
# #     "noticeTab": "CGYX",
# #     "keyword_all": "",
# #     "departmentName_all": "",
# #     "date1_all": "",
# #     "date2_all": "",
# #     "regionId_all": "640000"
# # }
# # session.post(url,data=data,headers=headers)
# # print(session.cookies)
# # session.get('http://www.ccgp-ningxia.gov.cn/TrafficStatistics.do',headers=headers)
# # print(session.cookies)
# # res = session.post('http://www.ccgp-ningxia.gov.cn//site/InteractionQuestion_findVNoticeNew.do',headers=headers)
# # print(res.cookies)
# # print(res.text)
# # print(session.cookies)
#
# # print('asdf'>'')
# with open('listxpath_second.html','r',encoding='utf-8') as f:
#     data = f.read()
# html = etree.HTML(data)
# ids = html.xpath('//div[@class="paddingSide15 bgGrey"]/table/tr[1]/td[1]/a/@id')
# print(ids)


# 6VHanuCwIIsWyhEJFtKjD%2fgFrxipu5rQBYp6gk15ZFVBjfL%2bW%2bMCcA%3d%3d

import urllib
from urllib import parse
# 6VHanuCwIIsWyhEJFtKjD%2fgFrxipu5rQBYp6gk15ZFVBjfL%2bW%2bMCcA%3d%3d
#
# 6VHanuCwIIsWyhEJFtKjD/gFrxipu5rQBYp6gk15ZFVBjfL+W+MCcA==
# 6VHanuCwIIsWyhEJFtKjD/gFrxipu5rQBYp6gk15ZFVBjfL+W+MCcA==

txt = '6VHanuCwIIsWyhEJFtKjD%2fgFrxipu5rQBYp6gk15ZFVBjfL%2bW%2bMCcA%3d%3d'
#URL解码
new_txt = urllib.parse.unquote(txt)
print(new_txt)