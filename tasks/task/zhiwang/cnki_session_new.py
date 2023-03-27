from datetime import datetime
from urllib.parse import urljoin, quote_plus
from lxml import etree
import ddddocr
import requests
import time

username = '15210559392'
password = 'mengyao2016'
session = requests.Session()

headers_init = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}

def login():

    img_retry = 1
    imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
    res = session.get(imgcode_url,headers=headers_init)
    with open('imgcode.jpg','wb') as f:
        f.write(res.content)
    code_str = get_checkcode('imgcode.jpg')
    print('验证码字符串为: ',code_str)
    _ = int(time.time()*1000)
    url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&checkCode={}&p=0&_={}'.format(username,password,code_str,_)
    res = session.get(url,headers=headers)
    if '验证码不正确' in res.text:
        if img_retry <= 5:
            print('验证码识别出错, 正在重新识别, 请稍后!!!')
            login()
            time.sleep(2)

    elif '登录失败，没有该用户' in res.text:
        print('请确认账号密码!')
    else:
        print('登录成功!!')
    return session
    # print(res.text)
    # print(session.cookies)

def get_checkcode(img):
    ocr = ddddocr.DdddOcr(old=True)
    # 第一个验证截图保存：verification_code_1.png
    with open(img, 'rb') as f:
        image = f.read()
    res = ocr.classification(image)
    return res

# session.cookies.pop('ASP.NET_SessionId')

url = 'https://kns.cnki.net/kns8/defaultresult/index'
session.get(url, headers=headers_init)
print(session.cookies)
session = login()
cookie_dblang = {
    "dblang":"ch"
}
session.cookies.update(cookie_dblang)
headers = {
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
# 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

# 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数
list_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
res = session.post(list_url, data=data, headers=headers)
html = etree.HTML(res.text)
searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
if searchsql_data:
    searchsql = searchsql_data[0]
else:
    searchsql = ''
print(session.cookies)

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

# 第二次获取根据日期排序的列表数据, 以下可改变页码来获取数据
res = session.post(list_url, data=params, headers=headers)
html = etree.HTML(res.text)
searchsql_data_new = html.xpath('//input[@id="sqlVal"]/@value')
if searchsql_data_new:
    searchsql_new = searchsql_data_new[0]
else:
    searchsql_new = ''
    print('searchsql为空, 代码有问题!!')
print('searchsql_new 为: ', searchsql_new)
params_2 = {
    'IsSearch': 'false',
    'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
    'SearchSql': searchsql_new,
    'PageName': 'defaultresult',
    'HandlerId': 5,
    'DBCode': 'CFLS',
    'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
    'CurPage': 1,
    'RecordsCntPerPage': 20,
    'CurDisplayMode': 'listmode',
    'CurrSortField': 'PT',
    'CurrSortFieldType': 'desc',
    'IsSortSearch': 'false',
    'IsSentenceSearch': 'false',
    'Subject': ''
}
res = session.post(list_url, data=params_2, headers=headers)
# print(res.text)
print(session.cookies)
html_list = etree.HTML(res.text)
pdf_urls = html_list.xpath('//td[@class="operat"]/a[1]/@href')

headers_pdf = {
    'Host': 'kns.cnki.net',
    'Connection': 'keep-alive',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
    'Upgrade-Insecure-Requests': '1',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'sec-ch-ua-platform': '"Windows"',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'
}
# hm_cookie = {
#     'Hm_lvt_d7c7037093938390bc160fc28becc542':'1661388015',
#     'Ecp_loginuserbk':'JY0004',
#     'Ecp_ClientIp':'223.71.72.248',
#     'Ecp_showrealname':'1',
#
# }
# session.cookies.update(hm_cookie)
# print(dir(res))
for pdf_url in pdf_urls:
    # cookie_ot =
    base_url = 'https://kns.cnki.net'
    pdf_url_new = urljoin(base_url,pdf_url)
    print(pdf_url_new)
    date = datetime.now()
    ot_data = date.strftime('%m/%d/%Y %H:%M:%S')
    print(ot_data)
    ot = quote_plus(ot_data).replace('+', '%20')
    print(ot)
    c_m_data = date.strftime('%Y-%m-%d %H:%M:%S')
    c_m = quote_plus(c_m_data).replace('+', '%20')
    print(c_m)
    cookie_part_update = {
        'Hm_lvt_d7c7037093938390bc160fc28becc542':'1661388015',
        'Ecp_ClientIp':'223.71.72.248',
        'Ecp_loginuserjf':'JY0004'
    }
    session.cookies.update(cookie_part_update)
    res = session.get(pdf_url_new,headers=headers_pdf)
    print(res.text)
    # res.encoding = 'gb2312'
    # print(res.text)
    # print(res.cookies)

    reditList = res.history
    print(f'获取重定向的历史记录：{reditList}')
    print(f'获取第一次重定向的headers头部信息：{reditList[0].headers}')
    # print(f'获取第一次重定向的返回的信息：{reditList[0].text}')
    print(f'获取重定向最终的url：{reditList[len(reditList) - 1].headers["location"]}')
    print(f'获取重定向最终的headers：{reditList[len(reditList) - 1].cookies}')
    redirect_url_1 = reditList[len(reditList) - 1].headers["location"]
    print(redirect_url_1)
    r = session.get(redirect_url_1,headers = headers_pdf)
    print(r.text)
    # print(reditList[len(reditList) - 1].headers["location"][41:77])
    # print('跳转至:', res.request.url)
    # print(session.cookies)
    break

print(session.cookies)