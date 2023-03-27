import json
import random
import re
import time
from datetime import datetime
from math import ceil

from task.chinesejournal.cur_identify import CurIdentify
from task.yiigle.login_tsg90 import LoginTrun
from task.SqlSave.mongo_store import MongoStore
from task.yiigle.redis_yii import YiRedis
from ..cur_identify import CurIdentify
from urllib.parse import quote

class Yiigle():

    def __init__(self):

        self.spider_at = 'win'
        self.mode = '全库'
        self.owning_account = '6849_扬州大学'
        self.identify = CurIdentify()
        self.login_obj = LoginTrun(self.owning_account)
        self.session, self.login_data = self.login_obj.login_page_turn(self.owning_account)
        # self.search_keywords = '糖尿病'
        # self.search_keywords = '细胞'
        self.tasks_path = './task/yiigle/yiigle_yangzhou_school_config.json'
        self.dir_pdfs = 'F:/yixuehui_pdfs'
        self.mongo_yii_all = MongoStore('wfhy_update', 'yii_all')
        self.mongo_yii_commit = MongoStore('wfhy_commit', 'yii_commit')
        self.redis_yii = YiRedis()
        # item 用于存储每篇文章的目标信息, 最后存入到数据库
        self.item = {}
        self.retry_down_pdf_max = 1
        self.retry_down_list_max = 5
        self.down_pdffail_num = 0
        self.list_fail_num = 0


    def update_task(self, condition, **kwargs):

        mode = condition['mode']
        keywords = condition['keywords']
        max_year = condition['max_year']
        min_year = condition['min_year']
        with open(self.tasks_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for index, search_info in enumerate(json_data):
            if search_info['mode'] == mode and search_info['keywords'] == keywords and search_info[
                'max_year'] == max_year and search_info['min_year'] == min_year:
                print(mode, keywords, kwargs)
                json_data[index].update(kwargs)
                print('这是更新后的json_data!!!')
        with open(self.tasks_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False))
            f.close()

    def get_search_info(self):
        '''
        获取执行任务的基本信息, 执行任务可以存在多个, 且排队做执行. 选择执行任务时, 任务队列需满足 owning_account(所属账号),have_end(未抓取过),is_running(没在执行),spider_at(抓取平台 win/linux), mode(抓取的方向 全库/病例), 符合这几个条件则进入任务队列排队执行
        :return: 返回self.search_infos 所有的待执行的任务搜索队列
        '''
        with open(self.tasks_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        new_list = []
        for base_info in json_data:
            if base_info['owning_account'] == self.owning_account and base_info['have_end'] != 1 and base_info['is_running'] != 1 and base_info['spider_at'] == self.spider_at and base_info['mode'] == self.mode:
                new_list.append(base_info)
        if new_list:
            self.search_infos = sorted(new_list, key=lambda x: x['level'], reverse=False)
            print('这是待抓取任务的优先级排序... ', self.search_infos)
            # self.search_infos = sorted_list[0]
            # self.update_task(self.search_info,have_start=1,is_running=1)

        else:
            print('任务都已经都在运行中/已完成了, 请注意查看并添加新的任务!!!')
            exit()


    def login_again(self):

        self.session.cookies.clear()
        self.session, self.login_data = self.login_obj.login_page_turn(self.owning_account)

    def get_page_num(self, year):
        '''
        获取最新搜索数据的最大页码, 与数据库中搜索数据最大页码做比较, 如果前者大于后者说明之前未抓取完成, 将数据库的最大页码作为待抓取的开始抓取页进行抓取,反之, 说明当前年已经抓取完成, 直接进入下一年进行数据抓取
        :param year: 当前列表页所属年份
        :return: 待抓取数据的最大及最小页码
        '''
        list_url = 'http://www.yiigle.yz.jd314.vip/apiVue/search/searchList'
        header_list = {
                "Host": "www.yiigle.yz.jd314.vip",
                "Connection": "keep-alive",
                "Content-Length": "214",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "http://www.yiigle.yz.jd314.vip",
                "Referer": "http://www.yiigle.yz.jd314.vip/Paper/Search?type=&q={}&searchType=pt".format(quote(self.search_info['keywords'])),
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                # "Cookie": "ddhgguuy_session=pnttq26b59q2fvvgl85nodjmr4; JSESSIONID=D94EF16C192F1A259C6C22C45F6C1224; JSESSIONID_CACHE=D94EF16C192F1A259C6C22C45F6C1224;  AWSALB=hbRkkDFgW3MEAP03BR2jvRfUxmNUSFbsfFB/K+Zwnk3Oa3Zk6I6o5sCqsjwu0Yj8zPDCyzeumK01xINKHCDeRzkqJH+ZiWo0cz4zJRAiuCr3a44OzboVUwjUNdfZ"
            }

        data = {
                "type": "",
                "sortField": "artPubDate",
                "page": 1,
                "searchType": "pt",
                "pageSize": self.search_info['page_size'],
                "queryString": "{}".format(self.search_info['keywords']),
                "query":" AND artPubYear:{}".format(year),
                "searchText": "{}".format(self.search_info['keywords']),
                "searchLog": "{}".format(self.search_info['keywords']),
                "isAggregations": "N",
                "logintoken": self.login_data['data']['clientUUID']
            }
        # data = {"type":"","sortField":"artPubDate","page":1,"searchType":"pt","pageSize":40,"queryString":"病","query":"","searchText":"病","searchLog":"病","isAggregations":"Y","logintoken":"dab5c1409f0c495bb3a3076bc8206d88"}
        print('这是cookies: ',self.session.cookies)
        print('这是data: ',data)
        print('这是headers: ',header_list)
        for i in range(10):
            try:
                res = self.session.post(list_url, json=data, headers=header_list,timeout=(20,30))
                res.encoding = 'utf-8'
                if res.status_code == 200 and res.json()['code'] == 200:
                    total = res.json()['data']['result']['searchTotal']
                    new_page_num = int(ceil(total // self.search_info['page_size'] + 1))
                    print('当前模块含有文章 {} 页, 共 {} 条'.format(new_page_num, total))
                    sql_page_num = int(self.find_mongo_page())
                    if sql_page_num == 0:
                        print('当前年数据未抓取过, 设置开始页码为: 1, 结束页码为: {}'.format(new_page_num))
                        min_page = 1
                        max_page = new_page_num + 1
                    elif sql_page_num < new_page_num:
                        min_page = sql_page_num
                        max_page = new_page_num + 1
                    elif sql_page_num >= new_page_num:
                        print('当前模块当前年已经抓取完成, 进入下一年')
                        return 'cur_year_have_spider'
                    else:
                        print('当前模块对比数据库最大页码与最新最大页码出现异常,退出, 请查看!!')
                        min_page = 0
                        max_page = 0
                        exit()
                    return min_page,max_page
                else:
                    if i >= 5:
                        print("超过5次获取列表页总页码失败, 暂停30~40min重新获取, 重新获取!!".format(i))
                        time.sleep(random.uniform(1800,2400))
                    else:
                        print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                        time.sleep(random.uniform(200,500))
            except:
                if i >= 5:
                    print("超过5次获取列表页总页码失败, 暂停30~40min重新获取, 重新获取!!".format(i))
                    time.sleep(random.uniform(1800, 2400))
                else:
                    print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                    time.sleep(random.uniform(200, 500))

    def find_mongo_page(self):
        '''
        根据账号和origin_moudle信息锁定待抓取当前年之前已经抓取过保存在数据库中的最大的页面
        :return:
        '''
        sql_page = self.mongo_yii_all.find_page_num(self.owning_account,self.item['origin_moudle'])
        print(sql_page)
        return sql_page


    def get_page_list(self, page, year):

        list_url = 'http://www.yiigle.yz.jd314.vip/apiVue/search/searchList'
        header_list = {
            "Host": "www.yiigle.yz.jd314.vip",
            "Connection": "keep-alive",
            "Content-Length": "214",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://www.yiigle.yz.jd314.vip",
            "Referer": "http://www.yiigle.yz.jd314.vip/Paper/Search?type=&q={}&searchType=pt".format(
                quote(self.search_info['keywords'])),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cookie": "ddhgguuy_session=pnttq26b59q2fvvgl85nodjmr4; JSESSIONID=D94EF16C192F1A259C6C22C45F6C1224; JSESSIONID_CACHE=D94EF16C192F1A259C6C22C45F6C1224;  AWSALB=hbRkkDFgW3MEAP03BR2jvRfUxmNUSFbsfFB/K+Zwnk3Oa3Zk6I6o5sCqsjwu0Yj8zPDCyzeumK01xINKHCDeRzkqJH+ZiWo0cz4zJRAiuCr3a44OzboVUwjUNdfZ"
        }

        data = {
            "type": "",
            "sortField": "artPubDate",
            "page": page,
            "searchType": "pt",
            "pageSize": self.search_info['page_size'],
            "queryString": "{}".format(self.search_info['keywords']),
            "query": " AND artPubYear:{}".format(year),
            "searchText": "{}".format(self.search_info['keywords']),
            "searchLog": "{}".format(self.search_info['keywords']),
            "isAggregations": "N",
            "logintoken": self.login_data['data']['clientUUID']
        }
        for i in range(self.retry_down_list_max):
            try:
                res = self.session.post(list_url, data=json.dumps(data), headers=header_list,timeout=(20,30))
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    list_items = res.json()['data']['result']['infos']
                    if len(list_items) > 0:
                        for item in list_items:
                            print('***' * 5 + '发现新数据' + '***' * 5)
                            self.item.clear()
                            self.item['art_id'] = item['artId']
                            self.item['detail_url'] = item['artUrl']
                            try:
                                date_temp = datetime.strptime(item['artPubDate'].split('T')[0],'%Y-%m-%d').date().strftime('%Y年%m月%d日')
                                self.item['date'] = date_temp
                            except:
                                self.item['date'] = '0000年00月00日'
                            self.item['title'] = item['artDropTitle']
                            self.item['owning_account'] = self.owning_account
                            self.item['file_name'] = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                                            self.item['title'])
                            md5_str = self.item['file_name'] + self.item['date']
                            status = self.redis_yii.set_item('yii', md5_str)
                            if status == 1:
                                file_path = self.dir_pdfs + '/' + self.item['file_name'] + '_' + self.item[
                                    'date'] + '.pdf'
                                self.item['origin'] = item['journalCn']
                                self.item['author'] = json.dumps(item['authorNames'], ensure_ascii=False)
                                # 为了与杭州师范字段统一, 这里将不存在的sitename用 columnCn代替
                                self.item['sitename'] = item['columnCn']
                                self.item['pyear'] = item['artPubYear']
                                self.item['cur_page'] = page
                                self.item['origin_moudle'] = '{}_{}_{}年_{}'.format(self.search_info['mode'],
                                                                                   self.search_info['keywords'],
                                                                                   self.cur_year,
                                                                                   self.search_info['spider_at'])
                                print('这是item: ', item)
                                self.down_pdf(file_path)
                                print('下载路径地址为: {}'.format(file_path))
                                print('开始识别医生信息...')
                                doctor_infos = self.identify.identify_pdf(file_path)
                                print('识别结果为: ', doctor_infos)
                                self.item.update(doctor_infos)
                                print("添加医生信息后的数据为: ", item)
                                self.save()
                            else:
                                print('已经抓取过当前数据, 不再抓取, 跳过!')
                                continue
                        break
                    else:
                        print('列表页没有文章数据了!! 可以跳过当前年, 抓取下一年数据!!')
                else:
                    print('列表页第 {} 页下载失败,暂停5秒钟, 重新下载!!'.format(page))
                    time.sleep(random.uniform(3, 10))
            except:
                print('请求列表页第 {} 次 出现问题, 暂停一会儿, 再次发起请求!!'.format(i))
                time.sleep(random.uniform(15,30))
            if i >= 3:
                print('请求列表页第 {} 次 出现问题, 休息10~20分钟重新登录并发起请求'.format(i))
                time.sleep(random.uniform(600,1200))

    def down_pdf(self, file_path):

        # 获取pdf连接地址
        post_url = 'http://www.yiigle.yz.jd314.vip/apiVue/transaction'
        data = {"productId":int(self.item['art_id']),"ProductType":"Tesis","type":2}
        headers = {
                    "Host": "www.yiigle.yz.jd314.vip",
                    "Connection": "keep-alive",
                    "Content-Length": "52",
                    "Accept": "application/json, text/plain, */*",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "token": "[object Object]",
                    "Content-Type": "application/json;charset=UTF-8",
                    "Origin": "http://www.yiigle.yz.jd314.vip",
                    "Referer": "http://www.yiigle.yz.jd314.vip/Paper/Search?type=&q={}&searchType=pt".format(quote(self.search_info['keywords'])),
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    # "Cookie": "ddhgguuy_session=pnttq26b59q2fvvgl85nodjmr4; JSESSIONID=B7495F1A04600D5132FCF628DB4BFE; JSESSIONID_CACHE=B7495F1A04600D5132FCF628DB4BFE; AWSALB=qfxufdNiNLpNfQ/HcHkQyXCDPQr/xEyEw8BeQe8Rf9ZFobgNSAyXekIc4b3dr8wth/+peToq4iddrTsUeG8eP9uijoQG7KBjrLAFHUXs+BWARhFpYGazmb8988Pf"
                }
        print('进入了pdf下载函数中!!')
        print('cookie为: ',self.session.cookies)
        JSESSIONID_CACHE = self.session.cookies.get('JSESSIONID')
        print('得到的JSESSIONID_CACHE 为: ',JSESSIONID_CACHE)

        self.session.cookies.set('JSESSIONID_CACHE',JSESSIONID_CACHE)
        print('更新后的cookie为: ',self.session.cookies)

        print('url为: ',post_url)
        print('headers为: ',headers)
        print('data为: ',data)
        res = self.session.post(post_url,data=json.dumps(data),headers=headers)
        print(res.text)
        exit()



        url = 'http://download.meddata.com.cn:8087/getCore/downloadCore?id={}&loginName={}&token={}'.format(
            self.item['art_id'], self.login_data['data']['loginName'], self.login_data['data']['token'])
        self.item['pdf_url'] = url
        headers = {
            "Host": "download.meddata.com.cn:8087",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://yiigle.meddata.d.jd314.vip/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        for i in range(self.retry_down_pdf_max):
            print('开始下载pdf文件...')
            try:
                res = self.session.get(url, headers=headers,timeout=(20,30))
                time.sleep(random.uniform(2,3))
                if res.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(res.content)
                        f.close()
                    print('pdf文件下载完成!!')
                    self.down_pdffail_num = 0
                    break
                else:
                    print('pdf文件下载失败第 {} 次, url 为 {} 信息为: {}, 等待一下重新下载'.format(i,url,file_path))
                    time.sleep(random.uniform(3,5))
            except:
                print('下载pdf文件第 {} 次读取失败或请求出错,不打紧再来!!'.format(i))
        else:
            print('下载pdf文件连续出错第 {} 次'.format(self.down_pdffail_num))
            self.down_pdffail_num += 1
        if self.down_pdffail_num >= 40:
            print('连续 40 个pdf文件下载失败, 可能遇到反爬, 休息30~40分钟后, 重新登录一下, 继续抓取!!')
            time.sleep(random.uniform(1800,2400))
            self.login_again()
            self.down_pdffail_num = 0

    def save(self):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        self.item['spider_date'] = spider_date

        self.mongo_yii_all.insert(self.item)
        if ('phones' in self.item) and self.item['phones']:
            print('发现新数据, 且存在手机号, 可以插入到commit表中')
            self.item['commit_status'] = '未提交'
            self.mongo_yii_commit.insert(self.item)
        else:
            print('检测到新数据, 但手机号为空, 不加入到commit表中')
        self.item.clear()

    def run(self):
        # print(self.session.cookies)
        # 获取待抓取任务的排序信息
        self.get_search_info()
        # 排队执行所有待抓取的任务
        for search_info in self.search_infos:
            self.search_info = search_info
            print('当前在抓取的任务信息为: ',self.search_info)
            time.sleep(5)
            for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):
                self.cur_year = year
                # self.update_task(self.search_info, have_start=1, is_running=1, cur_year=year)
                self.item['origin_moudle'] = '{}_{}_{}年_{}'.format(self.search_info['mode'],
                                                                   self.search_info['keywords'],
                                                                   self.cur_year,
                                                                   self.search_info['spider_at'])
                print('当前是 {} 年, 基本信息为: {}'.format(self.cur_year,str(self.search_info)))
                data = self.get_page_num(year)
                if data != 'cur_year_have_spider':
                    min_page,max_page = data
                    for page in range(min_page,max_page):
                        print('当前是 {} {} {}年 第 {} 页数据'.format(self.search_info['mode'], self.search_info['keywords'], year, page))
                        self.get_page_list(page, year)
                else:
                    print('开始抓取下一年数据!')
            self.update_task(self.search_info,have_end=1,is_running=0,cur_year=self.cur_year)