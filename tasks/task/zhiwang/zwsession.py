import time
import urllib
import requests


class ZwSession():

    def __init__(self):
        self.session = requests.Session()

    def get_foreign_data(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'Host': 'web.shutong.co:6443',
            'Referer': 'https://web.shutong.co:6443/kns/brief/Default_Result.aspx?code=SCDB',
            'sec-ch-ua-platform': 'Windows',
            'sec-ch-ua': 'Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin'
        }
        # 第一次请求
        first_url = 'https://web.shutong.co:6443/kns/Request/GetAptitude_searchHandler.ashx?action=Recommend_tip&kw=%E5%8C%BB%E9%99%A2&dbcode=SCDB&selectedField=%E5%8D%95%E4%BD%8D&valueFiled=SU%24%25%3D%7C%2CTKA%24%25%3D%7C%2CKY%24%3D%7C%2CTI%24%25%3D%7C%2CFT%24%25%3D%7C%2CAU%24%3D%7C%2CAF%24%25%2CAB%24%25%3D%7C%2CRF%24%25%3D%7C%2CCLC%24%3D%7C%3F%3F%2CLY%24%25%3D%7C%2CZCDOI%24%3D%7C%3F%2C&__=Mon%20Sep%2026%202022%2010%3A20%3A10%20GMT%2B0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'
        res_1 = self.session.get(first_url, headers=headers, verify=False)
        kns_cookie = {
            'KNS_SortType': ''
        }
        self.session.cookies.update(kns_cookie)

        # 第二次请求
        td = int(time.time() * 1000)
        second_url = 'https://web.shutong.co:6443/CRRS//RelItems.ashx?keyword=%E5%8C%BB%E9%99%A2&td={}'.format(td)
        res_2 = self.session.get(second_url, headers=headers)
        third_url = 'https://web.shutong.co:6443/kns/request/SearchHandler.ashx'
        third_data = {
            'action': '',
            'ua': '1.11',
            'isinEn': '1',
            'PageName': 'ASP.brief_default_result_aspx',
            'DbPrefix': 'SCDB',
            'DbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDBINDEX.xml',
            'db_opt': 'CJFQ,CJRF,CJFN,CDFD,CMFD,CPFD,IPFD,CCND,CISD,SNAD,CCJD',
            'txt_1_sel': 'AF$%',
            'txt_1_value1': '医院',
            'txt_1_special1': '%',
            'his': 0,
            'parentdb': 'SCDB',
            # '__': 'Mon Sep 26 2022 10:20:11 GMT+0800 (中国标准时间)'
        }

        # 第三次请求

        res_3 = self.session.post(third_url, headers=headers, data=third_data)

        # 第四次请求
        four_params = {
            'action': '1',
            'Param': 'ASP.brief_default_result_aspx#SCDB/主题#relevant/NVSM关键词,count(*)/NVSM关键词/(NVSM关键词,NVSM关键词)/40000/-/40/40000/ButtonView',
            'cid': '0',
            'clayer': '0',
            # '__':'Mon Sep 26 2022 10:20:11 GMT+0800 (中国标准时间)'
        }
        four_data = urllib.parse.urlencode(four_params, quote_via=urllib.parse.quote)
        four_url = 'https://web.shutong.co:6443/kns/group/doGroupLeft.aspx?{}'.format(four_data)
        res_4 = self.session.get(four_url, headers=headers)
        print(self.session.cookies)

        # 第五次请求之后可获取到英文数据

        five_url = 'https://web.shutong.co:6443/kns/brief/brief.aspx?pagename=ASP.brief_default_result_aspx&isinEn=1&dbPrefix=SCDB&dbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&research=off&t=1664158811448&keyValue=%E5%8C%BB%E9%99%A2&S=1&sorttype='
        res_5 = self.session.get(five_url, headers=headers)

        # print(res_5.text)

    def get_chinese_data(self):
        z_headers = {
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'Origin': 'https://web.shutong.co:6443',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://web.shutong.co:6443/kns/brief/Default_Result.aspx?code=SCDB'
        }

        # 中文第一次请求

        z_1_url = 'https://web.shutong.co:6443/kns/request/SearchHandler.ashx'
        z_1_data = {
            'action': '',
            'ua': '1.16',
            'ezflag': '1',
            'mixcode': 'SCDB',
            'resultSearch': '1',
            'isinEn': '1',
            'PageName': 'ASP.brief_default_result_aspx',
            'DbPrefix': 'CFLS',
            'DbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDBINDEX.xml',
            'db_opt': 'CJFQ,CJRF,CJFN,CDFD,CMFD,CPFD,IPFD,CCND,CISD,SNAD,CCJD',
            'txt_1_sel': 'AF$%',
            'txt_1_value1': '医院',
            'txt_1_special1': '%',
            'his': '0',
            'parentdb': 'SCDB',
            'research': 'on',
            '__': 'Mon Sep 26 2022 11:53:01 GMT+0800 (中国标准时间)'
        }
        res = self.session.post(z_1_url, headers=z_headers, data=z_1_data)
        # print(res.text)

        # 中文第二次请求
        z_2_data = {
            'action': 'webGroup',
            'ua': '1.16',
            'ezflag': '1',
            'mixcode': 'SCDB',
            'resultSearch': '1',
            'isinEn': '1',
            'PageName': 'ASP.brief_default_result_aspx',
            'DbPrefix': 'CFLS',
            'DbCatalog': '中国学术文献网络出版总库',
            'ConfigFile': 'SCDBINDEX.xml',
            'db_opt': 'CJFQ,CJRF,CJFN,CDFD,CMFD,CPFD,IPFD,CCND,CISD,SNAD,CCJD',
            'txt_1_sel': 'AF$%',
            'txt_1_value1': '医院',
            'txt_1_special1': '%',
            'his': '0',
            'parentdb': 'SCDB',
            'research': 'on',
            '__': 'Mon Sep 26 2022 11:53:01 GMT+0800 (中国标准时间)'
        }
        z_2_url = 'https://web.shutong.co:6443/kns/request/GetWebGroupHandler.ashx'
        res = self.session.post(z_2_url, headers=z_headers, data=z_2_data)
        # print(res.text)

        # 中文第三次请求, 可获取到中文数据
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        }

        z_3_url = 'https://web.shutong.co:6443/kns/brief/brief.aspx?curpage=12&RecordsPerPage=20&QueryID=12&ID=&turnpage=1&tpagemode=L&dbPrefix=CFLS&Fields=&DisplayMode=listmode&SortType=(%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2c%27TIME%27)+desc&PageName=ASP.brief_default_result_aspx&isinEn=1&'
        res = self.session.get(z_3_url, headers=headers)
        print(res.text)

    def get_session(self):
        '''
        知网的反爬是: 必须按照顺序模拟请求, 针对过程请求的验证, 有些链接请求后可以不返回数据, 但是必须要有请求, 这就是验证的过程, 另外知网并没有什么加密参数的破解, 按照顺序请求就可以了!! 流程是先进入主页开始请求英文数据, 返回后在此session基础上再去请求中文数据, 才能最终获取到数据
        :return: 携带有cookie的session, 每次session过期后将会重新获得最新session进行请求获取数据
        '''

        self.get_foreign_data()
        self.get_chinese_data()
        return self.session

    # def get_max_page(self):
    #
    #     headers = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    #     }
    #
    #     url = 'https://web.shutong.co:6443/kns/brief/brief.aspx?curpage=2&RecordsPerPage=20&QueryID=12&ID=&turnpage=1&tpagemode=L&dbPrefix=CFLS&Fields=&DisplayMode=listmode&SortType=(%e5%8f%91%e8%a1%a8%e6%97%b6%e9%97%b4%2c%27TIME%27)+desc&PageName=ASP.brief_default_result_aspx&isinEn=1&'
    #     res = self.session.get(z_3_url, headers=headers)
    #     print(res.text)


zwsession = ZwSession()
zwsession.get_session()
