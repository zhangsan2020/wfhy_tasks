import datetime

import requests
from lxml import etree

session = requests.Session()

url = 'https://ciac.zjw.sh.gov.cn/xmbjwsbsweb/xmquery/XmList.aspx'
headers_get = {

    'Host': 'ciac.zjw.sh.gov.cn',
    'Referer': 'http://www.shcpe.cn/',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'iframe',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}
res = session.get(url,headers=headers_get)
# print(res.text)
html = etree.HTML(res.text)
__EVENTVALIDATION = html.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]
__VIEWSTATE = html.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
__VIEWSTATEGENERATOR = html.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
__EVENTTARGET= 'gvXmList$ctl23$lbnNext'
print(__EVENTVALIDATION)
print(__VIEWSTATE)
print(__EVENTTARGET)

headers_post = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Length': '11242',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'ciac.zjw.sh.gov.cn',
    'Origin': 'https://ciac.zjw.sh.gov.cn',
    'Referer': 'https://ciac.zjw.sh.gov.cn/xmbjwsbsweb/xmquery/XmList.aspx',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Sec-Fetch-Dest': 'iframe',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

for page in (1,3):
    if page == 1:
        page = ''
    data = {
        '__EVENTTARGET': 'gvXmList$ctl23$lbnNext',
        '__EVENTARGUMENT': '',
        # '__EVENTARGUMENT':__EVENTTARGET,
        '__VIEWSTATE':__VIEWSTATE,
        '__VIEWSTATEGENERATOR':__VIEWSTATEGENERATOR,
        '__EVENTVALIDATION': __EVENTVALIDATION,
        'txtbjbh': '',
        'txtxmmc': '',
        'txtjsdw': '',
        'txtjsdd': '',
        'gvXmList$ctl23$inPageNum': page
    }

    res = session.post(url,data=data,headers=headers_post)
    print('当前是第 {} 页数据'.format(page))
    print(res.text)
    html = etree.HTML(res.text)
    __EVENTVALIDATION = html.xpath('//input[@id="__EVENTVALIDATION"]/@value')[0]
    __VIEWSTATE = html.xpath('//input[@id="__VIEWSTATE"]/@value')[0]
    __VIEWSTATEGENERATOR = html.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')[0]
    __EVENTTARGET = 'gvXmList$ctl23$lbnNext'
    print(__EVENTVALIDATION)
    print(__VIEWSTATE)
    print(__EVENTTARGET)
    with open(r'F:\wanfang_tasks\tasks\study_spider\shanghaijianshe\a.txt','a',encoding='utf-8') as f:
        f.write(str(datetime.datetime.now()))
        f.write('\n')
        f.write(res.text)