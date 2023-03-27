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
print(session.cookies)

cookie_dblang = {
    "dblang":"ch"
}
session.cookies.update(cookie_dblang)
headers_1 = {
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
'Accept': '*/*',
'X-Requested-With': 'XMLHttpRequest',
'sec-ch-ua-mobile': '?0',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
'sec-ch-ua-platform': 'Windows',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Dest': 'empty',
'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'
}
# res = session.get('https://kns.cnki.net/kns8/DefaultResult/_LoadSearchFields?dbcode=CFLS',headers=headers_1)
# print(res.text)
print(session.cookies)
res = session.get('https://recsys.cnki.net//RCDService/api/RecSysOpenApi/HotWordsStat?platformURL=kns.cnki.net%2Fkns8%40KNS8&statPeriod=week',headers=headers)
# print(res.text)
print(session.cookies)
# res = session.get('https://t.cnki.net/collect/quote/nzkpt',headers=headers)
# print(res.text)
# print(session.cookies)

headers_2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'sec-ch-ua-platform': 'Windows',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
    'Access-Control-Request-Method': 'GET',
    'Access-Control-Request-Headers': 'language,uniplatform,unitoken',
    'Origin': 'https://kns.cnki.net',
    'Host': 't.cnki.net'
}

res = session.options('https://t.cnki.net/collect/ux-api/v1/app/profile?appid=NZKPT',headers=headers_2)
# print(res.text)
print(session.cookies)

res = session.get('https://t.cnki.net/collect/ux-api/v1/app/profile?appid=NZKPT',headers=headers)
# print(res.text)
res = session.get('https://login.cnki.net/TopLoginNew/api/loginapi/IpLoginFlush?callback=jQuery111304914302446625163_1664265860716&_=1664265860717',headers=headers)
print(res.text)
print(session.cookies)
uid = re.findall('"Uid":"(.*?)",',res.text)[0]
print(uid)
data = {
    'uid':uid
}
res = session.post('https://kns.cnki.net/kns8/login/LoginIn',data=data,headers=headers_1)
print(res.text)

headers_3 = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'sec-ch-ua-platform': 'Windows',
    'Origin': 'https://kns.cnki.net',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'
}
#
data = {
    'IsSearch': 'true',
    'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
    'PageName': 'defaultresult',
    'DBCode': 'CFLS',
    'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
    'CurPage': '1',
    'RecordsCntPerPage': '20',
    'CurDisplayMode': 'listmode',
    'CurrSortField': '',
    'CurrSortFieldType': 'desc',
    'IsSentenceSearch': 'false',
    'Subject': ''
}
url_html_1 = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'

res = session.post(url_html_1, data=data, headers=headers_3)

html = etree.HTML(res.text)
searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
if searchsql_data:
    searchsql = searchsql_data[0]

print(searchsql)

params = {
    'IsSearch': 'false',
    'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
    'SearchSql': searchsql,
    'PageName': 'defaultresult',
    'HandlerId': '0',
    'DBCode': 'CFLS',
    'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
    'CurPage': 1,
    'RecordsCntPerPage': 20,
    'CurDisplayMode': 'listmode',
    'CurrSortField': 'PT',
    'CurrSortFieldType': 'desc',
    'IsSortSearch': 'true',
    'IsSentenceSearch': 'false',
    'Subject': ''
}
url_html_2 = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
res = session.post(url_html_2,data=params,headers=headers_3)
# print(res.text)
html = etree.HTML(res.text)
searchsql_data_new = html.xpath('//input[@id="sqlVal"]/@value')
if searchsql_data_new:
    searchsql_new = searchsql_data_new[0]

print('searchsql_new 为: ',searchsql_new)


data = {
    'PageName': 'defaultresult',
    'HandlerId': 5,
    'SearchSql': searchsql_data,
    'DBCode': 'CFLS',
    'CurItem': 121,
    'PageSize': 20
}
res = session.post('https://kns.cnki.net/kns8/Download/ValidRight',data=data,headers=headers_3)
print(res.text)

params_2 = {
    'IsSearch': 'false',
    'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
    'SearchSql': searchsql_new,
    'PageName': 'defaultresult',
    'HandlerId': 5,
    'DBCode': 'CFLS',
    'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
    'CurPage': 3,
    'RecordsCntPerPage': 20,
    'CurDisplayMode': 'listmode',
    'CurrSortField': 'PT',
    'CurrSortFieldType': 'desc',
    'IsSortSearch': 'false',
    'IsSentenceSearch': 'false',
    'Subject': ''
}

res = session.post(url_html_2,data=params_2,headers=headers_3)
print(res.text)