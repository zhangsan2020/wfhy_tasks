import json
import random
import re
import time
from datetime import datetime
from task.chinesejournal.cur_identify import CurIdentify
from task.yiigle.login_tsg90 import LoginTrun
from task.SqlSave.mongo_store import MongoStore
from task.yiigle.redis_yii import YiRedis
from ..cur_identify import CurIdentify


class Yiigle():

    def __init__(self):

        self.spider_at = 'win'
        self.mode = '全库'
        # self.owning_account = '6849_杭州师范大学附属医院'
        self.owning_account = '6849_浙江中医药大学'

        self.identify = CurIdentify()
        self.login_obj = LoginTrun(self.owning_account)
        self.session, self.login_data = self.login_obj.login_page_turn(self.owning_account)
        # self.search_keywords = '糖尿病'
        # self.search_keywords = '细胞'
        self.tasks_path = './task/yiigle/yiigle_hzsf_config.json'
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
        self.have_spider_num = 0
        self.have_spider_num_max = 255
        self.turn_page_num = 5
        self.identify_failed = 0
        self.identify_failed_limit = 52


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
        list_url = 'http://zdcsxylsrijgoieurjhgfo.98tsg.com/getCore/manyElements'
        header_list = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "479",
            "Content-Type": "application/json",
            # "Cookie": "Hm_lvt_04b5e4d6892791247a01f35935d692be=1670286856,1670291708,1670375260,1672812177; _trs_uv=lco916ox_5355_2ja3; authdomain=AuthDomain.tsg211.com",
            "electronicPublicationStatus": "0",
            "Host": "zdcsxylsrijgoieurjhgfo.98tsg.com",
            "Origin": "http://zdcsxylsrijgoieurjhgfo.98tsg.com",
            "Referer": "http://zdcsxylsrijgoieurjhgfo.98tsg.com/",
            "token": "{}".format(self.login_data['data']['loginName']),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

        data = {
            "pageNo": 1,
            "pageSize": self.search_info['page_size'],
            "condition": {
                "main": "{}".format(self.search_info['keywords']),
                "author": "",
                "authorCom": "",
                "periodicalName": "",
                "yearStage": "",
                "yearList": [str(year)],
                "journalTypeList": [],
                "sorting": "发表时间",
                # "retrieve": " (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1"
            }
        }
        for i in range(10):
            res = self.session.post(list_url, data=json.dumps(data), headers=header_list,timeout=(20,30))
            res.encoding = 'utf-8'
            if res.status_code == 200:
                new_page_num = res.json()['pages']
                total = res.json()['total']
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

    def find_mongo_page(self):
        '''
        根据账号和origin_moudle信息锁定待抓取当前年之前已经抓取过保存在数据库中的最大的页面
        :return:
        '''
        sql_page = self.mongo_yii_all.find_page_num(self.owning_account,self.item['origin_moudle'])
        print(sql_page)
        return sql_page


    def get_page_list(self,year):

        list_url = 'http://zdcsxylsrijgoieurjhgfo.98tsg.com/getCore/manyElements'
        header_list = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "479",
            "Content-Type": "application/json",
            # "Cookie": "Hm_lvt_04b5e4d6892791247a01f35935d692be=1670286856,1670291708,1670375260,1672812177; _trs_uv=lco916ox_5355_2ja3; authdomain=AuthDomain.tsg211.com",
            "electronicPublicationStatus": "0",
            "Host": "zdcsxylsrijgoieurjhgfo.98tsg.com",
            "Origin": "http://zdcsxylsrijgoieurjhgfo.98tsg.com",
            "Referer": "http://zdcsxylsrijgoieurjhgfo.98tsg.com/",
            "token": "{}".format(self.login_data['data']['loginName']),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

        data = {
            "pageNo": self.cur_page,
            "pageSize": self.search_info['page_size'],
            "condition": {
                "main": "{}".format(self.search_info['keywords']),
                "author": "",
                "authorCom": "",
                "periodicalName": "",
                "yearStage": "",
                "yearList": [str(year)],
                "journalTypeList": [],
                "sorting": "发表时间",
                # "retrieve": " (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1"
            }
        }
        for i in range(self.retry_down_list_max):
            try:
                time.sleep(random.uniform(2,5))
                res = self.session.post(list_url, data=json.dumps(data), headers=header_list,timeout=(20,30))
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    list_items = res.json()['list'][0]['resultList']
                    if len(list_items) > 0:
                        for item in list_items:
                            print('***' * 5 + '发现新数据' + '***' * 5)
                            self.item.clear()
                            self.item['art_id'] = item['id']
                            self.item['detail_url'] = 'http://zdcsxylsrijgoieurjhgfo.98tsg.com/#/details?id=' + item['id']
                            self.item['date'] = item['pubDate'].replace('年', '-').replace('月', '-').replace('日', '')
                            self.item['title'] = item['titleCN']
                            self.item['owning_account'] = self.owning_account
                            self.item['file_name'] = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                                            self.item['title']).replace('fontcolorred', '').replace(
                                'font', '') + '_' + self.item['date'] + '.pdf'
                            # md5_str = self.item['file_name'] + '_' + self.item['date'] + '.pdf'
                            status = self.redis_yii.set_item('yii', self.item['file_name'])
                            # if self.down_pdffail_num >= 5 and self.have_spider_num >= 255:
                            #     print('当前年 pdf文件下载失败次数超过 5 次, 且')
                            if status == 1:
                                self.have_spider_num = 0
                                file_path = self.dir_pdfs + '/' + self.item['file_name']
                                self.item['origin'] = item['periodicalName']
                                self.item['author'] = json.dumps(item['authorList'], ensure_ascii=False)

                                self.item['sitename'] = item['crawlSiteName']
                                self.item['pyear'] = item['pyear']
                                self.item['cur_page'] = self.cur_page
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
                                if doctor_infos['identify_status'] == '识别失败':
                                    self.identify_failed += 1
                                    print('当前是连续第 {} 次识别pdf文件失败!'.format(self.identify_failed))
                                    if self.identify_failed > self.identify_failed_limit:
                                        print('连续超过 {} 次识别pdf文件失败, 可能遇到了反爬, 等待1~2min, 重新登录一下!!'.format(self.identify_failed_limit))
                                        time.sleep(random.uniform(60,120))
                                        self.login_again()
                                        self.identify_failed = 0
                                else:
                                    self.identify_failed = 0
                                self.item.update(doctor_infos)
                                print("添加医生信息后的数据为: ", item)
                                self.save()
                            else:
                                self.have_spider_num += 1
                                print('连续抓取过数据第 {} 个, 继续抓取, 跳过!'.format(self.have_spider_num))
                                if self.have_spider_num > self.have_spider_num_max:
                                    print('连续抓取过数据超过 {} 个, 向后跳 {} 页, 继续抓取!'.format(self.have_spider_num_max,self.turn_page_num))
                                    self.cur_page += self.turn_page_num
                                    self.have_spider_num = 0
                                    return 'turn_over'
                                continue
                            # print('***' * 5 + '发现新数据' + '***' * 5)
                        break
                    else:
                        print('列表页没有文章数据了!! 可以跳过当前年, 抓取下一年数据!!')
                else:
                    print('列表页第 {} 页下载失败,暂停5秒钟, 重新下载!!'.format(self.cur_page))
                    time.sleep(random.uniform(3, 10))
            except:
                print('请求列表页第 {} 次 出现问题, 暂停5~10分钟, 再次发起请求!!'.format(i))
                time.sleep(random.uniform(300,600))
            if i >= 3:
                print('请求列表页第 {} 次 出现问题, 休息30~40分钟重新登录并发起请求'.format(i))
                time.sleep(random.uniform(1800,2400))
                self.login_again()
                # res = self.session.post(list_url, data=json.dumps(data), headers=header_list)

    def down_pdf(self, file_path):

        url = 'http://download.meddata.com.cn:8087/getCore/downloadCore?id={}&loginName={}&token={}'.format(
            self.item['art_id'], self.login_data['data']['loginName'], self.login_data['data']['token'])
        self.item['pdf_url'] = url
        headers = {
            "Host": "download.meddata.com.cn:8087",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://zdcsxylsrijgoieurjhgfo.98tsg.com/",
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
                print('下载pdf文件第 {} 次链接读取失败或请求出错,不打紧再来!!'.format(i))
        else:
            print('下载pdf文件连续出错第 {} 次, 休息一下, Go on!!!'.format(self.down_pdffail_num))
            self.down_pdffail_num += 1
            time.sleep(random.uniform(1,3))
        if self.down_pdffail_num >= 30:
            print('连续 30 个pdf文件下载失败, 可能遇到反爬, 休息2~3分钟后, 向后跳 {} 页, 继续抓取!!'.format(self.turn_page_num))
            time.sleep(random.uniform(120,180))
            # self.login_again()
            self.cur_page += self.turn_page_num
            self.down_pdffail_num = 0
            return 'turn_over'

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
        for i in range(3):
            try:
                # 获取待抓取任务的排序信息
                self.get_search_info()
                # 排队执行所有待抓取的任务
                for search_info in self.search_infos:
                    self.search_info = search_info
                    print('当前在抓取的任务信息为: ',self.search_info)
                    time.sleep(5)
                    for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):

                        self.cur_year = year
                        self.update_task(self.search_info, have_start=1, is_running=1, cur_year=year)
                        self.item['origin_moudle'] = '{}_{}_{}年_{}'.format(self.search_info['mode'],
                                                                           self.search_info['keywords'],
                                                                           self.cur_year,
                                                                           self.search_info['spider_at'])
                        print('当前是 {} 年, 基本信息为: {}'.format(self.cur_year,str(self.search_info)))

                        data = self.get_page_num(year)
                        if data != 'cur_year_have_spider':
                            # 进入新的一年后, 将已经抓去过数据数量设置为 0
                            min_page,max_page = data
                            self.cur_page = min_page
                            while self.cur_page < max_page:
                            # for page in range(min_page,max_page):
                                print('当前是{} {} {} {}年 第 {} 页数据'.format(self.owning_account,self.search_info['mode'], self.search_info['keywords'], year, self.cur_page))
                                spider_status = self.get_page_list(year)
                                if spider_status == 'turn_over':
                                    print('检测到当前发生了页面跳过, 跳转之后的页码为: {}'.format(self.cur_page))
                                    time.sleep(random.uniform(2,5))
                                self.cur_page += 1
                        else:
                            print('开始抓取下一年数据!')
                    self.update_task(self.search_info,have_end=1,is_running=0,cur_year=self.cur_year)
                break
            except Exception as e:
                print('抓取时出现问题, 休息10~15分钟, 详情为: {}'.format(repr(e)))
                time.sleep(random.uniform(600,900))