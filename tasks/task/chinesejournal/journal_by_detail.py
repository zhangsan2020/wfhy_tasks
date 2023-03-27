import json
import os
import re
import time

from .loginfromtsg import LoginTrun


class ChinaJournal(LoginTrun):

    def __init__(self):

        super().__init__()
        self.login_page_turn()
        self.first_list_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index'
        self.dir_pdfs = 'F:/weipu_pdfs/'

    def get_page_list(self):

        param = '{"ObjectType":1,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"","ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"Y=手术","Sort":"2","SortField":null,"UserID":"15856445","PageNum":7,"PageSize":20,"SType":null,"StrIds":null,"IsRefOrBy":0,"ShowRules":"  参考文献=手术  ","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":456979,"AdvTabGuid":""}'
        data = {'searchParamModel':param}
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Search/SearchList?searchParamModel='+param
        print('这是列表页URL: ',url)

        headers = {
                "Accept": "text/html, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                "Referer": self.first_list_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"
            }
        res = self.session.post(url,data=data,headers=headers)
        print(res.text)
        print(res.status_code)

    def get_detail(self,detail_id):
        '''
        返回获取pdf连接地址的必须参数数据
        :param detail_id:
        :return:
        '''
        detail_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id={}'.format(detail_id)
        headers_detail = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "jiangnan.webvpn.jingshi2015.com:8181",
            "Referer": 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        res = self.session.get(detail_url, headers=headers_detail)
        print('这是详情页数据', res.text)
        infos = re.findall('vpn_rewrite_js\(\(function \(\) \{ showdown\(&#39;(\d+)&#39;,&#39;(.*?)&#39;\)',res.text)
        print('这是info 数据: ',infos)
        if infos:
            print('获取到infos数据为: ',infos)
            info_data = infos[0][1]
            time_ = str(int(time.time() * 1000))
            data = {
                'id': detail_id,
                'info': info_data,
                'ts': time_,
            }
            return data
        else:
            return self.get_detail(detail_id)

    def get_pdf_url(self,data):

        detail_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id={}'.format(data['id'])
        print('这是 detail_url: ', detail_url)
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/ArticleDown'

        headers = {
                    "Accept": "*/*",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                    "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                    "Referer": detail_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest"
                }

        print(data)
        res = self.session.post(url,headers=headers,data=data)
        print('这是detail结果',res.text)
        print(res.status_code)
        if res.status_code == 200:
            print('正常获取到pdfURL连接地址!!')
            return res.json()
        else:
            return self.get_pdf_url(data)

    def down_pdf(self,url_info):

        print('这是url_info: ',url_info)
        url = url_info['url']
        headers = {
                "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Referer": "http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id=7108212568",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }

        res = self.session.get(url,headers=headers)
        file_path = os.path.join(self.dir_pdfs, 'a.pdf')
        with open(file_path,'wb') as f:
            f.write(res.content)
            f.close()
        print(res.text)


    def run(self):
        # self.enterlist()
        # self.before_page_list()
        self.get_page_list()
        data = self.get_detail('7108212568')
        url_info = self.get_pdf_url(data)
        self.down_pdf(url_info)