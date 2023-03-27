import json
import re

import requests
from lxml import etree

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
url = 'https://kns.cnki.net/kns8/defaultresult/index'
res = session.get(url, headers=headers)


# print(res.text)
# print(session.cookies)
# 获取cookie  sid
session.get('https://login.cnki.net/members/scripts/top.js?v=20220921',headers=headers)

# 获取 cookie sid与 cookie SID_tuijian
session.get('https://tuijian.cnki.net/a/quote/ad.js',headers=headers)
session.get('https://tuijian.cnki.net/a/quote/ad.js',headers=headers)

# 获取cookie SID_recsys

session.get('https://recsys.cnki.net//RCDService/api/RecSysOpenApi/HotWordsStat?platformURL=kns.cnki.net%2Fkns8%40KNS8&statPeriod=week',headers=headers)

cookie_dblang = {
    "dblang":"ch"
}
session.cookies.update(cookie_dblang)
# 获取SID_t
session.options('https://t.cnki.net/collect/ux-api/v1/app/profile?appid=NZKPT',headers=headers)
print(session.cookies)
# # 删除 cookies ASP.NET_SessionId
# session.cookies.pop('ASP.NET_SessionId')
# # 更新ASP.NET_SessionId
# session.get('https://login.cnki.net/TopLoginNew/scripts/json2-min.js?v=220923',headers=headers)
# # 更新ASP.NET_SessionId
# session.get('https://login.cnki.net/TopLoginNew/content/index.css?v=220923',headers=headers)

# 更新 SID_t
session.get('https://t.cnki.net/collect/ux-api/v1/app/profile?appid=NZKPT',headers=headers)
# 更新ASP.NET_SessionId
session.get('https://login.cnki.net/TopLoginNew/scripts/members/toplogin2.js?v=220923',headers=headers)

res = session.get('https://login.cnki.net/TopLoginNew/api/loginapi/IpLoginFlush?callback=jQuery111304914302446625163_1664265860716&_=1664265860717',headers=headers)
print(session.cookies)
print(res.text)
uid = re.findall('"Uid":"(.*?)",',res.text)[0]
print(uid)
print(session.cookies)
print(session.cookies.get_dict())
data = {
    'uid':uid
}
session.get('https://kns.cnki.net/favicon.ico',headers=headers)
print(session.cookies)
part_data = json.loads(session.cookies.get_dict()['Ecp_LoginStuts'])
r = part_data['r']
Ecp_loginuserbk = part_data['UserName']
print(r)
part_cookies = {
    'Ecp_notFirstLogin':r,
    'Ecp_loginuserbk':Ecp_loginuserbk,

}
headers_new = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'
}
session.cookies.update(part_cookies)
print(session.cookies.get_dict())
res = session.post('https://kns.cnki.net/kns8/login/LoginIn',data=data,headers=headers_new)
print(res.text)
# print(session.cookies)
# session.get('https://kns.cnki.net/favicon.ico',headers=headers)
# print(session.cookies)
# headers_fina = {
#     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#     'X-Requested-With': 'XMLHttpRequest',
#     'sec-ch-ua-mobile': '?0',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
#     'sec-ch-ua-platform': 'Windows',
#     'Origin': 'https://kns.cnki.net',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-Mode': 'cors',
#     'Sec-Fetch-Dest': 'empty',
#     'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'
# }
# #
# data = {
#     'IsSearch': 'true',
#     'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
#     'PageName': 'defaultresult',
#     'DBCode': 'CFLS',
#     'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
#     'CurPage': '1',
#     'RecordsCntPerPage': '20',
#     'CurDisplayMode': 'listmode',
#     'CurrSortField': '',
#     'CurrSortFieldType': 'desc',
#     'IsSentenceSearch': 'false',
#     'Subject': ''
# }
# finally_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
#
# res = session.post(finally_url, data=data, headers=headers_fina)
# # print(res.text)
# # print(session.cookies)
# # # def get_searchsql():
# html = etree.HTML(res.text)
# searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
# if searchsql_data:
#     searchsql = searchsql_data[0]
# # # if searchsql_data:
# # #     searchsql = searchsql_data[0]
# # #     return searchsql
# # # else:
# # print(searchsql)
# #
# # # get_searchsql()
# #
# params = {
#     'IsSearch': 'false',
#     'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
#     'SearchSql': searchsql,
#     'PageName': 'defaultresult',
#     'HandlerId': '0',
#     'DBCode': 'CFLS',
#     'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
#     'CurPage': 1,
#     'RecordsCntPerPage': 20,
#     'CurDisplayMode': 'listmode',
#     'CurrSortField': 'PT',
#     'CurrSortFieldType': 'desc',
#     'IsSortSearch': 'true',
#     'IsSentenceSearch': 'false',
#     'Subject': ''
# }
# url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
# res = session.post(url,data=params,headers=headers)
# print(res.text)