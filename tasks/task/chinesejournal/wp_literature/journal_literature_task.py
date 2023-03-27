import json
import os
import random
import re
import time
import urllib.parse
from datetime import datetime
from urllib import parse
from task.chinesejournal.cur_identify import CurIdentify
from lxml import etree
from task.chinesejournal.loginfromtsg import LoginTrun
# from ..common.useragent import useragent_pool
from requests.exceptions import ConnectionError,ReadTimeout
from task.SqlSave.mongo_store import MongoStore
from task.chinesejournal.redis_wp import WpRedis


class ChinaJournal():

    def __init__(self):

        self.login_obj = LoginTrun()
        self.session = self.login_obj.login_page_turn()
        self.identify = CurIdentify()
        self.wp_redis = WpRedis()
        self.wp_mongo_commit = MongoStore('wfhy_commit','wp_commit')
        self.wp_mongo_update = MongoStore('wfhy_update','wp_all')
        # 当前已表格模式进行数据抓取, 模式每页显示50条数据, 没办法重置
        # self.search_info = {'mode': '参考文献', 'keywords': '手术', 'max_year': 2022, 'min_year': 2009, 'max_page': 300,'page_size': 50}
        self.tasks_path = './task/common/weipu_config.json'
        self.dir_pdfs = 'F:/weipu_pdfs/'
        # http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/
        self.first_list_url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index'
        self.detail_url_format = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id={}'
        # self.useragent = random.choice(useragent_pool)
        # 连续第多少次重新下载, 如果检测到列表页面中detail与pdf连续10次之前被下载过, 将不再对当前模块发起请求, 直接接入下一模块
        self.havedown_times = 1
        self.havedown_times_max = 200
        self.item = {}
        # 筛选逻辑是: 在当前任务中, 找出没有完成的(have_end=0)且没在执行中的任务(is_running=0),对这些任务根据优先级别(level越小级别越高)做排序,选择出当前任务!! 每次程序结束时更新任务列表中的任务状态!!
        self.get_search_info()
        # self.exception_wait_seconds = random.randint(3,10)


    def update_task(self,condition,**kwargs):

        mode = condition['mode']
        keywords = condition['keywords']
        max_year = condition['max_year']
        min_year = condition['min_year']
        with open(self.tasks_path,'r',encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for index,search_info in enumerate(json_data):
            if search_info['mode'] == mode and search_info['keywords'] == keywords and search_info['max_year'] == max_year and search_info['min_year'] == min_year:
                print(mode,keywords,kwargs)
                json_data[index].update(kwargs)
                print('这是更新后的json_data!!!')
        with open(self.tasks_path,'w',encoding='utf-8') as f:
            f.write(json.dumps(json_data,ensure_ascii=False))
            f.close()


    def get_search_info(self):

        with open(self.tasks_path,'r',encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        new_list = []
        for search_info in json_data:
            if search_info['have_end'] != 1 and search_info['is_running'] != 1:
                new_list.append(search_info)
                # b2 = sorted(, key=lambda x: x['age'], reverse=True)
        if new_list:
            sorted_list = sorted(new_list, key=lambda x: x['level'], reverse=False)
            print('这是排序中的sorted_list',sorted_list)
            self.search_info = sorted_list[0]
            # self.update_task(self.search_info,have_start=1,is_running=1)

        else:
            print('任务都已经都在运行中/已完成了, 请注意查看并添加新的任务!!!')
            exit()


    def login(self):

        if 'session_token' in self.session.cookies.get_dict():
            print('老的cookie为: ', self.session.cookies.get_dict())
            self.session.cookies.clear()
        self.session = self.login_obj.login_page_turn()
        print('这是新的 cookie: ', self.session.cookies.get_dict())
    # def get_first_page_list(self):

    def get_page_list(self, year, page_num):

        param = '{{"ObjectType":1,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"YY={year}#{year}","ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"Y={keywords}","Sort":2,"SortField":null,"UserID":"15856445","PageNum":{page_num},"PageSize":{page_size},"SType":null,"StrIds":null,"IsRefOrBy":0,"ShowRules":"  年份={year}   AND   {mode}={keywords}  ","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":3490,"AdvTabGuid":""}}'.format(
            year=year, keywords=self.search_info['keywords'], page_num=page_num, page_size=self.search_info['page_size'],
            mode=self.search_info['mode'])
        data = {'searchParamModel': param}
        url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Search/SearchList?searchParamModel=' + param
        print('这是列表页URL: ', url)

        headers = {
            "Accept": "text/html, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "883",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Origin": "http://sdu.webvpn.jingshi2015.com:8383",
            "Referer": self.first_list_url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        try:
            res = self.session.post(url, data=data, headers=headers, timeout=(5, 10))
        except:
            print('列表页请求出现问题,等待一下, 重新请求!!')
            time.sleep(random.randint(2,10))
            res = self.session.post(url, data=data, headers=headers, timeout=(5, 10))
        if res.status_code == 200:
            print('列表页数据获取正常!!')
            html = etree.HTML(res.text)
            trs = html.xpath('//div[@id="list"]/table/tbody/tr')
            # print(len(article_infos))
            if trs:
                for tr in trs:
                    # print(article_info)
                    can_down = ''.join(tr.xpath('./td[@class="source"]/div//a/text()'))
                    article_title = tr.xpath('./td[@class="title"]/a/text()')[0].strip()
                    year = tr.xpath('./td[@class="cited"][1]/text()')[0].strip()
                    file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",article_title) +  year + '.pdf'
                    if '下载PDF' in can_down:
                        duplicate_status = self.wp_redis.set_item('wp_file_name', file_name)
                        # time.sleep(random.uniform(0.1, 0.3))
                        if duplicate_status == 1:
                            self.havedown_times = 1
                            # print('连续已下载第 {} 次'.format(self.havedown_times))
                            self.item.clear()
                            detail_id = tr.xpath('./td[@class="title"]/a/@articleid')[0].strip()
                            detail_url = self.detail_url_format.format(detail_id)
                            authors = ';'.join(tr.xpath('./td[@class="t-left"][1]/a/text()')).strip()
                            source_name = ';'.join(tr.xpath('./td[@class="t-left"][2]/a/text()')).strip()
                            reference_num = tr.xpath('./td[@class="cited"][2]/text()')[0].strip()
                            self.item['file_name'] = file_name
                            self.item['detail_url'] = detail_url
                            self.item['authors'] = authors
                            self.item['source_name'] = source_name
                            self.item['year'] = year
                            self.item['reference_num'] = reference_num
                            url_info = self.get_pdf_url(detail_id, article_title)
                            # 下载pdf文件
                            file_path = self.down_pdf(url_info)
                            # 识别pdf数据
                            self.identify_data(file_path)
                            print('这是items: ', self.item)
                            # 保存数据
                            self.save()
                        else:
                            # print('之前已经抓取过,跳过!')
                            self.havedown_times += 1
                            if self.havedown_times >= self.havedown_times_max:
                                print('连续已抓取数据超过 {} 次, 跳过当前年!!!'.format(self.havedown_times_max))
                                self.havedown_times = 0
                                return 0
                            print('连续已抓取数据第 {} 次'.format(self.havedown_times))
                            continue
                    else:
                        print('当前article没有pdf下载选项, 跳过, 标题为: ', article_title)
            else:
                print('当前列表页没有数据了, 开始进入下一年!!')
                return 0
        else:
            print('列表页请求数据失败, 重新获取列表页数据!!')
            time.sleep(10)
            self.get_page_list(year, page_num)

    def get_detail(self, detail_id, article_title):

        '''
        返回获取pdf连接地址的必须参数数据
        :param detail_id:
        :return:
        '''
        detail_url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id={}'.format(detail_id)
        headers_detail = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Referer": 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        try:
            res = self.session.get(detail_url, headers=headers_detail, timeout=(10, 20))
        except:
            print('详情页下载失败, 等待一下, 重新开始下载')
            time.sleep(random.randint(2, 10))
            res = self.session.get(detail_url, headers=headers_detail, timeout=(10, 20))
        # print(res.text)
        if res.status_code == 200:
            time.sleep(random.uniform(0, 0.5))
            # print('这是详情页数据', res.text)
            # infos = re.findall('vpn_rewrite_js\(\(function \(\) \{ showdown\(.*?,&#39;(.*?)&#39;\)',res.text)
            infos = re.findall('vpn_rewrite_js\(\(function \(\) \{ showdown\(.*?,&#39;(.*?)&#39;\)',res.text)

            print('这是infos 数据: ', infos)
            if infos:
                # print('获取到infos数据为: ', infos)
                time_ = str(int(time.time() * 1000))
                data = {
                    'params': {
                        'id': detail_id,
                        'info': infos[0],
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

        login_url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/RegistLogin/CheckUserIslogin?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5M.YrXmDZUlDZfE7D5yYghkWPHyCX21S7wBNZFI66Mi4dT65jp.xafj37dCuFUzQJ0TR3u_TrejOPuAofsZwROGMD.PTdzU_YBnnEPFLb4wcSbPPwSAU6zpzC6tGUZtmBrg5mL6j4upkBy2gz0raA3BgfWPs.kz7EVkhBd88PGN_V6EYVibPla1GDjID7qVT3yskcRhAXKzg95yW42z0ozU.IgvgmcEqqx1PrKxlXg5hI20I3dV.awKnNohHln4IGV88WX.8Son5zbwVmbLY3uvpbOlB6GOjKiMCnR1bkvR2MO_98u_8bbsy0l3f0MhuLE3Y9lkhjUYu.0nN495V3ik_Uhfn_wCoJnxeXwyDFFkbhxj7biire37PAzxJyN3fZ5I_Q1fbj62yZAiq0cxEndA'
        headers_login = {
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Connection": "keep-alive",
            "Content-Length": "0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "http://sdu.webvpn.jingshi2015.com:8383",
            "Referer": "http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id=7107214622",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        res = self.session.post(login_url, data={}, headers=headers_login)
        print('判断登录返回: ', res.text)

        data = {
            'articleId': detail_id
        }
        url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/RegistLogin/CheckUserIslogin?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5dKq3tR9XrA5gnvbgR0tKOo7IdYC4_L1s4EGAZdV0_1hwX.dn4qNZj_yctZwwG0uPOtHUNScb0W9QnNVSXL_PtfayATRh5DnE3loGSRfT7Qi5EdTeMhBxgR5eliUY1YuhgjAYClNXEF3fvDIs8Eu8YioPWGVOxJP9Qerz66mCkuWgVx7Gu.8n4pznQMCdYuQdYehqckB4glKiGGFSMN.O5.VnMLOHbV12wu51VJnOmWRHb75Ly37dSXzFFleJf_ssTbSr2XQqUyuQyirKtCL.oLU2JTOGWVjbUcD_D41RC9VR5vyuTlCY_mHpD687hHgvLPP6D.4eI84_XNV8zulwrj7Irk84Vi7R3MEBiZ_MWP8m3ab4Z18rm35UHxiTImsJFuwT6T2RLbmlzUUwLjdNVa'

        res = self.session.post(url, data=json.dumps(data))
        print('这是before_pdf_url: ', res.text)
        vpn_timestamp = str(int(time.time() * 1000))
        r = self.session.get(
            'http://sdu.webvpn.jingshi2015.com:8383/wengine-vpn/cookie?method=get&host=cstj.cqvip.com&scheme=http&path=/Qikan/Article/Detail&vpn_timestamp={}'.format(
                vpn_timestamp))
        print(r.text)

    def get_pdf_url(self, detail_id, article_title):

        url_param = self.get_detail(detail_id, article_title)
        # self.before_pdf_url(url_param['params']['id'])
        url_param['params']['ts'] = str(int(time.time() * 1000))
        detail_url = self.detail_url_format.format(url_param['params']['id'])
        print('这是 detail_url: ', detail_url)
        url_param['params']['info'] = parse.quote(url_param['params']['info'])
        print('这是url_param: ', url_param)

        url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/ArticleDown?id={}&info={}&ts={}'.format(url_param['params']['id'],url_param['params']['info'] , url_param['params']['ts'])
        # id=3669701&info=AtZeRpSg6jxonUUrhCd89Qb%252ftpg6ze4bSKjIkPQtrqA%253d&ts=1672101269667
        headers = {
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Connection": "keep-alive",
            # "Content-Length": "100",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "http://sdu.webvpn.jingshi2015.com:8383",
            "Referer": detail_url,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            res = self.session.post(url, headers=headers, data=url_param['params'], timeout=(5, 10))
        except Exception as e:
            print('下载url请求出现异常, 等待一下, 重新发起请求!!! 错误为: {}'.format(repr(e)))
            time.sleep(random.randint(2,10))
            res = self.session.post(url, headers=headers, data=url_param['params'], timeout=(5, 10))

        time.sleep(random.uniform(0, 0.5))
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
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": self.first_list_url,
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        try:
            time.sleep(random.uniform(1,3))
            res = self.session.get(url, headers=headers, timeout=(5, 10))
            print('下载pdf文件的状态码是: {}'.format(res.status_code))
            if res.status_code == 200:
                file_path = os.path.join(self.dir_pdfs, self.item['file_name'])
                with open(file_path, 'wb') as f:
                    f.write(res.content)
                    f.close()
                time.sleep(random.uniform(0.1, 0.5))
                print('下载成功!!')
                return file_path
            else:
                print('下载pdf连接地址状态码不为 200, text为: ',res.text)
                print(res.text)
                self.down_pdf(url_info)
        except:
            # self.lo

            wait_seconds = random.randint(3,30)
            print('pdf文件下载失败! 暂停 {} 秒钟,重新下载'.format(wait_seconds))
            time.sleep(wait_seconds)
            self.down_pdf(url_info)

    def identify_data(self,file_path):

        print('下载路径地址为: {}'.format(file_path))
        print('开始识别医生信息...')
        doctor_infos = self.identify.identify_pdf(file_path)
        print('识别结果为: ', doctor_infos)
        self.item.update(doctor_infos)

    def save(self):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        self.item['spider_date'] = spider_date
        self.item['origin_moudle'] = '{}_{}_{}'.format(self.search_info['mode'],self.search_info['keywords'],self.cur_year)
        self.wp_mongo_update.insert(self.item)
        if ('phones' in self.item) and self.item['phones']:
            print('发现新数据, 且存在手机号, 可以插入到commit表中')
            self.item['commit_status'] = '未提交'
            self.wp_mongo_commit.insert(self.item)
        else:
            print('检测到新数据, 但手机号为空, 不加入到commit表中')

    def run(self):

        for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):
            self.cur_year = str(year)
            for page in range(10, self.search_info['max_page']):
                print('当前是 {} 年, {}, {}, 第 {} 页'.format(year,self.search_info['mode'],self.search_info['keywords'],page))
                print('基本信息为: {}'.format(str(self.search_info)))
                status = self.get_page_list(year, page)
                if status == 0:
                    print('{} 年已经抓取完成, 进入下一年!!'.format(year))
                    break
        print('当前任务已经完成,更新任务配置文件!!!')
        self.update_task(self.search_info,have_end=1,is_running=0)