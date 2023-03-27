import time

import requests
from lxml import etree

session = requests.Session()

headers_init = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}
url = 'https://kns.cnki.net/kns8/defaultresult/index'
res = session.get(url, headers=headers_init, timeout=(5,20))
print(res.text)
t = int(time.time() * 1000)
post_url = 'https://kns.cnki.net/kns8/defaultresult/index'
data = {
    'txt_1_sel':'AF$%',
    'kw':	'%E5%8C%BB%E9%99%A2',
    'txt_1_value1':	'医院',
    'txt_1_special1':'%',
    'txt_extension'	:'',
    'currentid'	:'txt_1_value1',
    'dbJson'	:'coreJson',
    'dbPrefix'	:'',
    'db_opt':	'CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN',
    'singleDB':	'',
    'db_codes'	:'CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN',
    'singleDBName'	:'',
    'againConfigJson'	:'false',
    'action'	:'scdbsearch',
    'ua':	'1.11',
    't':	t
}

headers = {
    'Host': 'kns.cnki.net',
    'Connection':'keep-alive',
    # 'Content-Length': 407
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://www.cnki.net',
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://www.cnki.net/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
}

res = session.post(post_url,data=data,headers=headers)
print(res.text)

headers_1 = {
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
    'Accept-Encoding': 'gzip, deflate, br'
}
print('进来了')
headers_0 = {
    'Host': 't.cnki.net',
    'Connection': 'keep-alive',
    'Accept': '*/*',
    'Access-Control-Request-Method': 'POST',
    'Access-Control-Request-Headers': 'content-type,language,uniplatform,unitoken',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
    'Accept-Encoding': 'gzip, deflate, br'
}
time_ = int(time.time() * 1000)

# data0 = {"data":[{"m":"M22","f":"M2201","a":"M220101","d":"作者单位","r":"","t":time_},{"m":"M22","f":"M2201","a":"M220103","d":"","r":"","t":time_}],"appId":"NZKPT"}

res = session.options('https://t.cnki.net/collect/ux-api/v1/app/batch-trace', headers=headers_0)
headers_3 = {
    'Host': 't.cnki.net',
    'Connection': 'keep-alive',
    'Content-Length': '178',
    'unitoken': '',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'uniplatform': 'NZKPT',
    'language': '',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Accept': '*/*',
    'sec-ch-ua-platform': '"Windows"',
    'Origin': 'https://www.cnki.net',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://www.cnki.net/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9'
    # {unitoken: '', uniplatform: 'NZKPT', language: ''}

}
# headers_3 = {
#     'uniplatform': 'NZKPT',
#     'language': '',
#     'unitoken': '',
#     'Content-Type': 'application/json',
# }
data0 = {"data": [{"m": "M10", "f": "M1004", "a": "M100401", "d": "", "r": "", "t": time_}], "appId": "NZKPT"}
res = session.post('https://t.cnki.net/collect/ux-api/v1/app/batch-trace', headers=headers_3, data=data0)
print(res.text)

# res = session.get('https://kns.cnki.net/kns8/DefaultResult/_LoadSearchFields?dbcode=CFLS',headers=headers_3)
# print(res.text)
res = session.get('https://recsys.cnki.net//RCDService/api/RecSysOpenApi/HotWordsStat?platformURL=kns.cnki.net%2Fkns8%40KNS8&statPeriod=week',headers=headers_1)
print(res.text)
# exit()
# 获取大的搜索模块基本数据
header_field = {
    'Referer': 'https://www.cnki.net/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
}
field_json_url = 'https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6'
res = session.get(field_json_url,headers=header_field)
print(res.text)
# jsondata = re.findall('var fieldJsonN=(.*)', res.text)[0].replace(';','').replace('Key:','"key":').replace('Value:','"Value":').replace('FieldList:','"FieldList":').replace('ColName:','"ColName":').replace('Text:','"Text":')
# # print(jsondata)
# db_model = search_first_match(jsondata,searchinfo['model'])
# print(db_model)

# exit()
queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}'
data = {
    'IsSearch': 'true',
    'QueryJson': queryjson,
    'PageName': 'defaultresult',
    'DBCode': 'CFLS',
    'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
    'CurPage': 1,
    'RecordsCntPerPage': 20,
    'CurDisplayMode': 'listmode',
    'CurrSortField': '',
    'CurrSortFieldType': 'desc',
    'IsSentenceSearch': 'false',
    'Subject': ''
}
# print('*'*20)
# print('这是要看的data: {}'.format(str(data)))
# print('*' * 20)
# 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

# 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数
# get_resulturl_data()

if res.status_code == 200 and ('题名' in res.text and '发表时间' in res.text):
    html = etree.HTML(res.text)
    searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
    if searchsql_data:
        searchsql = searchsql_data[0]
        searchsql = searchsql
        retry_getsearchsql = 0

# get_resulturl_data()
url_2 = 'https://kns.cnki.net/kns8/Group/Result'
data = {
    'queryJson':'{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}"'
}
headers_2 = {
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
    'Accept-Encoding': 'gzip, deflate, br',
    'Origin': 'https://kns.cnki.net',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'

}
res = session.post(url_2,data=data,headers=headers_2)
print(res.text)