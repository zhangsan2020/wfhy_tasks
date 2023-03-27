import json
import os
import re
import time

from lxml import etree

from .loginfromtsg import LoginTrun


class ChinaJournal(LoginTrun):

    def __init__(self):

        super().__init__()
        self.login_page_turn()
        self.first_list_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index'
        self.dir_pdfs = 'F:/weipu_pdfs/'
        self.searchinfo = {'mode': '参考文献', 'keywords': '手术', 'max_year':2022, 'min_year':2009, 'max_page':51,'page_size':100}


    def get_page_list(self,year,page_num):

        # param = '{"ObjectType":1,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"","ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"Y=手术","Sort":"2","SortField":null,"UserID":"15856445","PageNum":2,"PageSize":20,"SType":null,"StrIds":null,"IsRefOrBy":0,"ShowRules":"参考文献=手术","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":4,"AdvTabGuid":""}'
        param = '{{"ObjectType":1,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"YY={year}#{year}","ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"Y={keywords}","Sort":"2","SortField":null,"UserID":"15856445","PageNum":{page_num},"PageSize":{page_size},"SType":null,"StrIds":null,"IsRefOrBy":0,"ShowRules":"  年份={year}   AND   {mode}={keywords}  ","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":4466,"AdvTabGuid":""}}'.format(year=year,keywords=self.searchinfo['keywords'],page_num=page_num,page_size=self.searchinfo['page_size'],mode=self.searchinfo['mode'])
        data = {'searchParamModel':param}
        print('这是列表页data参数: ',data)
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Search/SearchList?searchParamModel='+param
        print('这是列表页URL: ',url)

        headers = {
                    "Accept": "text/html, */*; q=0.01",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Length": "883",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                    "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                    "Referer": self.first_list_url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest"
                }
        res = self.session.post(url,data=data,headers=headers)
        # print(res.text)
        print(res.status_code)
        if res.status_code == 200:
            print('列表页数据获取正常!!')
            html = etree.HTML(res.text)
            # article_infos = html.xpath('//div[@class="simple-list"]//a[contains(text(),"下载PDF")]/@onclick')
            article_infos = html.xpath('//div[@class="simple-list"]/dl')
            print(len(article_infos))
            for article_info in article_infos:
                print(article_info)
                article_title = article_info.xpath('./dt/a/text()')[0]
                article_pdf = article_info.xpath('.//a[contains(text(),"下载PDF")]/@onclick')
                if article_pdf:
                    article_data = re.findall("showdown\('(\d+)','(.*?)'\)",article_pdf[0])
                    print(article_title,article_data)
                    if article_data:
                        print('切割列表页下载pdf动作数据正常！！')
                        time_ = str(int(time.time() * 1000))
                        data = {
                            'id': article_data[0][0],
                            'info': article_data[0][1],
                            'ts': time_,
                            'article_title':article_title
                        }
                        url_info = self.get_pdf_url(data)
                        print('这是获取到的pdf_url: ',url_info)
                        self.down_pdf(url_info)
                    else:
                        print('切割列表页下载pdf动作数 error！！请查看')
                else:
                    print('当前article没有pdf下载选项, 跳过, 标题为: ', article_title)

        else:
            print('列表页请求数据失败, 重新获取列表页数据!!')
            time.sleep(10)
            self.get_page_list(year,page_num)


    def get_pdf_url(self,data):

        # detail_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id={}'.format(data['id'])
        # print('这是 detail_url: ', detail_url)
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/ArticleDown?id={}&info={}&ts={}'.format(data['id'],data['info'],data['ts'])

        headers = {
                    "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                    "Connection": "keep-alive",
                    "Content-Length": "108",
                    "Accept": "*/*",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                    "Referer": 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=Qikan_Search_Index',
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }

        print(data)
        res = self.session.post(url,headers=headers,data=json.dumps(data))
        print('这是detail结果',res.text)
        print(res.status_code)
        if res.status_code == 200:
            print('正常获取到pdfURL连接地址!!')
            url_info = res.json()
            url_info['article_title'] = data['article_title']
            return url_info
        else:
            print('获取pdf url数据错误!!')
            time.sleep(2)
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
                "Referer": self.first_list_url,
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }

        res = self.session.get(url,headers=headers)
        file_path = os.path.join(self.dir_pdfs, '{}.pdf'.format(url_info['article_title']))
        with open(file_path,'wb') as f:
            f.write(res.content)
            f.close()
        # print(res.text)


    def run(self):
        # self.enterlist()
        # self.before_page_list()
        for year in range(self.searchinfo['max_year'],self.searchinfo['min_year'],-1):
            self.cur_year = str(year)
            for page in range(1,self.searchinfo['max_page']):
                print('当前是 {} 年, 基本信息为: {}'.format(year,str(self.searchinfo)))
                self.get_page_list(year,page)
                # data = self.get_detail('7108212568')
                # url_info = self.get_pdf_url(data)
                # self.down_pdf(url_info)