import random

import requests
from .zwcookie import ZwCookie
from ..common.useragent import useragent_pool

class ShuTong():

    def __init__(self):

        self.session = requests.Session()
        self.zwcookie = ZwCookie()

    def get_session(self):

        cookies_maxpage = self.zwcookie.get_cookies()
        cookies = cookies_maxpage['cookies']
        maxpage = cookies_maxpage['maxpage']
        session_cookies = {}
        for cookie in cookies:
            session_cookies[cookie['name']] = cookie['value']
        print(session_cookies)
        self.session.cookies.update(session_cookies)
        return maxpage
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        # }
        # list_url = 'https://web.shutong.co:6443/kns/brief/brief.aspx?curpage=2&RecordsPerPage=20&QueryID=11&ID=&turnpage=1&tpagemode=L&dbPrefix=CFLS&Fields=&DisplayMode=listmode&SortType=(FFD%2c%27RANK%27)+desc&PageName=ASP.brief_default_result_aspx&isinEn=1&'
        # r = self.session.get(list_url, headers=headers, verify=False)
        # print(r.text)
        # self.session.cookies.update(cookies)

    def downloader(self,url):

        headers = {
            'User-Agent' : random.choice(useragent_pool)
        }
        res = self.session.get(url,headers=headers,verify=False)
        if res.status_code == 200 and '发表时间' in res.text:
            print('请求列表页数据成功!!')
            return res.text
        else:
            print('请求失败, 重新生成session发起请求')
            data = self.downloader(url)
            return data


    def run(self):

        maxpage = self.get_session()
        list_url_format = 'https://web.shutong.co:6443/kns/brief/brief.aspx?curpage={}&RecordsPerPage=20&QueryID=11&ID=&turnpage=1&tpagemode=L&dbPrefix=CFLS&Fields=&DisplayMode=listmode&SortType=(FFD%2c%27RANK%27)+desc&PageName=ASP.brief_default_result_aspx&isinEn=1&'
        for i in range(1,2):
            list_url = list_url_format.format(i)
            data = self.downloader(list_url)
            print(data)