import json
import os
import random
import re
import time
from urllib import parse
from .cur_identify import CurIdentify
from lxml import etree
from .loginfromtsg import LoginTrun
from ..common.useragent import useragent_pool
from requests.exceptions import ConnectionError,ReadTimeout


class ChinaJournal():

    def __init__(self):

        self.login_obj = LoginTrun()
        self.session = self.login_obj.login_page_turn()
        self.first_list_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index'
        self.dir_pdfs = 'F:/weipu_pdfs/'
        self.searchinfo = {'mode': '参考文献', 'keywords': '手术', 'max_year': 2022, 'min_year': 2009, 'max_page': 51,'page_size': 100}
        # self.useragent = random.choice(useragent_pool)
        self.identify = CurIdentify()
        self.detail_url_format = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id={}'
        self.item = {}

    def get_page_list(self, year, page_num):

        param = '{{"ObjectType":1,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"YY={year}#{year}","ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"Y={keywords}","Sort":"2","SortField":null,"UserID":"15856445","PageNum":{page_num},"PageSize":{page_size},"SType":null,"StrIds":null,"IsRefOrBy":0,"ShowRules":"  年份={year}   AND   {mode}={keywords}  ","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":4466,"AdvTabGuid":""}}'.format(
            year=year, keywords=self.searchinfo['keywords'], page_num=page_num, page_size=self.searchinfo['page_size'],
            mode=self.searchinfo['mode'])
        data = {'searchParamModel': param}
        print('这是列表页data参数: ', data)
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Search/SearchList?searchParamModel=' + param
        print('这是列表页URL: ', url)

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
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            "X-Requested-With": "XMLHttpRequest"
        }
        res = self.session.post(url, data=data, headers=headers, timeout=(5, 10))
        # print(res.text)
        # print(res.status_code)
        if res.status_code == 200:
            print('列表页数据获取正常!!')
            html = etree.HTML(res.text)
            # article_infos = html.xpath('//div[@class="simple-list"]//a[contains(text(),"下载PDF")]/@onclick')
            article_infos = html.xpath('//div[@class="simple-list"]/dl')
            # print(len(article_infos))
            for article_info in article_infos:
                # print(article_info)
                article_title = article_info.xpath('./dt/a/text()')[0]
                article_pdf = article_info.xpath('.//a[contains(text(),"下载PDF")]/@onclick')
                if article_pdf:
                    article_data = re.findall("showdown\('(\d+)','(.*?)'\)", article_pdf[0])
                    print(article_title, article_data)
                    if article_data:
                        self.item.clear()
                        # print('切割列表页下载pdf动作数据正常！！')
                        detail_id = article_data[0][0]
                        # self.item['detail_url'] = self.detail_url_format.format(detail_id)
                        # url_param = self.get_detail(detail_id, article_title)
                        url_info = self.get_pdf_url(detail_id, article_title)
                        # 下载pdf文件
                        file_path = self.down_pdf(url_info)
                        self.identify_data(file_path)
                        # 识别pdf文件数据
                        # self.id

                    else:
                        print('切割列表页下载pdf动作数 error！！请查看')
                else:
                    print('当前article没有pdf下载选项, 跳过, 标题为: ', article_title)

        else:
            print('列表页请求数据失败, 重新获取列表页数据!!')
            time.sleep(3)
            self.get_page_list(year, page_num)

    def get_detail(self, detail_id, article_title):

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
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        res = self.session.get(detail_url, headers=headers_detail, timeout=(5, 10))
        if res.status_code == 200:
            time.sleep(random.uniform(0, 1))
            # print('这是详情页数据', res.text)
            infos = re.findall('vpn_rewrite_js\(\(function \(\) \{ showdown\(&#39;(\d+)&#39;,&#39;(.*?)&#39;\)',res.text)
            print('这是info 数据: ', infos)
            if infos:
                # print('获取到infos数据为: ', infos)
                info_data = infos[0][1]
                time_ = str(int(time.time() * 1000))
                data = {
                    'params': {
                        'id': detail_id,
                        'info': info_data,
                        'ts': time_,
                    },
                    'article_title': article_title
                }
                return data
            else:
                return self.get_detail(detail_id, article_title)
        else:
            return self.get_detail(detail_id, article_title)

    def before_pdf_url(self, detail_id):

        login_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/RegistLogin/CheckUserIslogin?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5M.YrXmDZUlDZfE7D5yYghkWPHyCX21S7wBNZFI66Mi4dT65jp.xafj37dCuFUzQJ0TR3u_TrejOPuAofsZwROGMD.PTdzU_YBnnEPFLb4wcSbPPwSAU6zpzC6tGUZtmBrg5mL6j4upkBy2gz0raA3BgfWPs.kz7EVkhBd88PGN_V6EYVibPla1GDjID7qVT3yskcRhAXKzg95yW42z0ozU.IgvgmcEqqx1PrKxlXg5hI20I3dV.awKnNohHln4IGV88WX.8Son5zbwVmbLY3uvpbOlB6GOjKiMCnR1bkvR2MO_98u_8bbsy0l3f0MhuLE3Y9lkhjUYu.0nN495V3ik_Uhfn_wCoJnxeXwyDFFkbhxj7biire37PAzxJyN3fZ5I_Q1fbj62yZAiq0cxEndA'
        headers_login = {
            "Host": "jiangnan.webvpn.jingshi2015.com:8181",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
            "Referer": "http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id=7107214622",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        res = self.session.post(login_url, data={}, headers=headers_login)
        print('判断登录返回: ', res.text)

        data = {
            'articleId': detail_id
        }
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/RegistLogin/CheckUserIslogin?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5dKq3tR9XrA5gnvbgR0tKOo7IdYC4_L1s4EGAZdV0_1hwX.dn4qNZj_yctZwwG0uPOtHUNScb0W9QnNVSXL_PtfayATRh5DnE3loGSRfT7Qi5EdTeMhBxgR5eliUY1YuhgjAYClNXEF3fvDIs8Eu8YioPWGVOxJP9Qerz66mCkuWgVx7Gu.8n4pznQMCdYuQdYehqckB4glKiGGFSMN.O5.VnMLOHbV12wu51VJnOmWRHb75Ly37dSXzFFleJf_ssTbSr2XQqUyuQyirKtCL.oLU2JTOGWVjbUcD_D41RC9VR5vyuTlCY_mHpD687hHgvLPP6D.4eI84_XNV8zulwrj7Irk84Vi7R3MEBiZ_MWP8m3ab4Z18rm35UHxiTImsJFuwT6T2RLbmlzUUwLjdNVa'

        res = self.session.post(url, data=json.dumps(data))
        print('这是before_pdf_url: ', res.text)
        vpn_timestamp = str(int(time.time() * 1000))
        r = self.session.get(
            'http://jiangnan.webvpn.jingshi2015.com:8181/wengine-vpn/cookie?method=get&host=cstj.cqvip.com&scheme=http&path=/Qikan/Article/Detail&vpn_timestamp={}'.format(
                vpn_timestamp))
        print(r.text)

    def get_pdf_url(self, detail_id, article_title):

        url_param = self.get_detail(detail_id, article_title)
        # self.before_pdf_url(url_param['params']['id'])
        url_param['params']['ts'] = str(int(time.time() * 1000))
        detail_url = self.detail_url_format.format(url_param['params']['id'])
        self.item['detail_url'] = detail_url
        print('这是 detail_url: ', detail_url)
        url_param['params']['info'] = parse.quote(url_param['params']['info'])
        print('这是url_param: ', url_param)

        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/ArticleDown?id={}&info={}&ts={}'.format(url_param['params']['id'],url_param['params']['info'] , url_param['params']['ts'])
        # id=3669701&info=AtZeRpSg6jxonUUrhCd89Qb%252ftpg6ze4bSKjIkPQtrqA%253d&ts=1672101269667
        headers = {
            "Host": "jiangnan.webvpn.jingshi2015.com:8181",
            "Connection": "keep-alive",
            # "Content-Length": "100",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
            "Referer": detail_url,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            res = self.session.post(url, headers=headers, data=url_param['params'], timeout=(5, 10))
        except Exception as e:
            print('下载url请求出现异常, 暂停3秒钟, 重新发起请求!!! 错误为: {}'.format(repr(e)))
            time.sleep(3)
            res = self.session.post(url, headers=headers, data=url_param['params'], timeout=(5, 10))

        time.sleep(random.uniform(0, 1))
        if res.status_code == 200:
            print('***' * 20)
            print('正常获取到pdfURL连接地址!!')
            print('***' * 20)
            url_info = res.json()
            url_info['article_title'] = url_param['article_title']
            return url_info
        else:
            print('获取pdf url数据错误!!')
            time.sleep(2)
            return self.get_pdf_url(detail_id, article_title)

    def down_pdf(self, url_info):

        print('这是url_info: ', url_info)
        url = url_info['url']
        headers = {
            "Host": "jiangnan.webvpn.jingshi2015.com:8181",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": self.first_list_url,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            res = self.session.get(url, headers=headers, timeout=(5, 10))
            print('下载pdf文件的状态码是: {}'.format(res.status_code))
            if res.status_code == 200:
                time.sleep(random.uniform(0, 1))
                file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                   url_info['article_title'] + '.pdf')
                file_path = os.path.join(self.dir_pdfs, file_name)
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                    f.close()
                return file_path
            else:
                self.down_pdf(url_info)
        except ConnectionError:
            print('pdf文件下载失败! 暂停3秒钟,重新下载')
            time.sleep(3)
            self.down_pdf(url_info)

    def identify_data(self,file_path):

        print('下载路径地址为: {}'.format(file_path))
        print('开始识别医生信息...')
        doctor_infos = self.identify.identify_pdf(file_path)
        print('识别结果为: ', doctor_infos)


    def run(self):

        for year in range(self.searchinfo['max_year'], self.searchinfo['min_year'], -1):
            self.cur_year = str(year)
            for page in range(1, self.searchinfo['max_page']):
                print('当前是 {} 年, 基本信息为: {}'.format(year, str(self.searchinfo)))
                self.get_page_list(year, page)
