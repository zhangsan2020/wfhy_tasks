import copy
import json
import random
import re
import time
from datetime import datetime
from task.chinesejournal.cur_identify import CurIdentify
from task.common.login_tsg90 import LoginTrun
from ..yii_mongo import YiiMongo
from task.yiigle.redis_yii import YiRedis
from task.common.cur_identify import CurIdentify


class Yiigle():

    def __init__(self):

        self.spider_at = 'win'
        self.mode = '作者单位'
        # self.mode = '病例'

        # self.owning_account = '6849_杭州师范大学附属医院'
        self.owning_account = '6849_杭州师范大学'
        self.domain = 'hzsf66nkjgdrngkedrgnkdrfjgnkd.98tsg.com'
        self.identify = CurIdentify()
        self.login_obj = LoginTrun(self.owning_account)
        self.session, self.login_data = self.login_obj.login_page_turn(self.owning_account)
        # self.search_keywords = '糖尿病'
        # self.search_keywords = '细胞'
        self.tasks_path = './task/yiigle/yiigle_hzsf_config.json'
        self.dir_pdfs = 'F:/yixuehui_pdfs'
        self.mongo_yii_all = YiiMongo('wfhy_update', 'yii_all')
        self.mongo_yii_commit = YiiMongo('wfhy_commit', 'yii_commit')
        self.redis_yii = YiRedis()
        self.redis_all_phones = YiRedis()
        # item 用于存储每篇文章的目标信息, 最后存入到数据库
        self.item = {}
        self.retry_down_pdf_max = 1
        self.retry_down_list_max = 5
        self.down_pdffail_num = 0
        self.list_fail_num = 0
        self.have_spider_num = 0
        self.have_spider_num_max = 255
        self.turn_page_num = 2
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


    def check_task_info(self,search_info):

        with open(self.tasks_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for task_info in json_data:
            task_info_compare = '{}_{}_{}_{}'.format(task_info['mode'],task_info['keywords'],task_info['max_year'],task_info['min_year'])
            search_info_compare = '{}_{}_{}_{}'.format(search_info['mode'],search_info['keywords'],search_info['max_year'],search_info['min_year'])
            if task_info['mode'] == self.mode:
                if task_info_compare == search_info_compare:
                    print('锁定到当前任务!!')
                    if task_info['is_running'] == 1:
                        print('检测到当前任务正在抓取中, 跳过!!')
                    elif task_info['have_end'] == 1:
                        print('检测到当前任务已经抓取完成,跳过')
                    else:
                        return 'task_can_do'
                else:
                    print('找不到即将要抓取的任务了, 请问您是不是把它给删除了!!!')
            else:
                print('任务平台不对,跳过!!')

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
            if base_info['mode'] == self.mode and base_info['have_end'] != 1 and base_info['is_running'] != 1:
                new_list.append(base_info)
        if new_list:
            search_infos = sorted(new_list, key=lambda x: x['level'], reverse=False)
            print('这是待抓取任务的优先级排序... ', search_infos)
            for search_info in search_infos:
                task_status = self.check_task_info(search_info)
                if task_status == 'task_can_do':
                    yield search_info

        else:
            print('任务都已经都在运行中/已完成了, 请注意查看并添加新的任务!!!')
            exit()

    def login_again(self):

        self.session.cookies.clear()
        self.session, self.login_data = self.login_obj.login_page_turn(self.owning_account)

    def request_list(self):
        list_url = 'http://{}/getCore/manyElements'.format(self.domain)
        header_list = {
            "Host": self.domain,
            "Connection": "keep-alive",
            "Content-Length": "496",
            "Accept": "application/json, text/plain, */*",
            "electronicPublicationStatus": "0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "token": "hzsfdx",
            "Content-Type": "application/json",
            "Origin": "http://{}".format(self.domain),
            "Referer": "http://{}/".format(self.domain),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "pageNo": 1,
            "pageSize": 50,
            "condition": {
                "main": "",
                "author": "",
                "authorCom": "",
                "periodicalName": "",
                "yearStage": "",
                "yearList": [self.cur_year],
                "journalTypeList": [],
                "sorting": "发表时间",
                "retrieve": " authorCom:*{}* AND pYear:[* TO *] AND start:1 AND !isChMeAss:\"4\" AND !isChMeAss:\"4\" AND start:1 AND !isChMeAss:\"4\" AND start:1 AND !isChMeAss:\"4\" AND start:1 AND !isChMeAss:\"4\" AND start:1".format(self.keywords_)
            }

        }
        print('开始发起列表页请求, 目的是获取模块页码数据!!')
        for i in range(self.retry_down_list_max):
            # try:
            time.sleep(random.uniform(3, 5))
            try:
                res = self.session.post(list_url, json=data, headers=header_list, timeout=(20, 30))
                print('get_page_num数据请求正常')
            except Exception as e:
                print('请求获取get_page_num时出现错误: {}!!重新获取'.format(repr(e)))
                time.sleep(random.uniform(2, 5))
                if i >= 2:
                    print('获取 最大页码时 连续超过2次出错, 重新登录获取数据!!!')
                    self.login_again()
                continue
            res.encoding = 'utf-8'
            if res.status_code == 200 and '请重新进入' not in res.text:
                new_page_num = res.json()['pages']
                total = res.json()['total']
                print('当前模块含有文章 {} 页, 共 {} 条'.format(new_page_num, total))
                return total,new_page_num
            elif '抱歉，暂无数据' in res.text:
                print('当前模块没有数据,进入下一模块')
                return 'no_data'
            else:
                if i >= 5:
                    print("超过5次获取列表页总页码失败, 暂停一会儿, 重新获取, 重新登录获取!!".format(i))
                    time.sleep(random.uniform(600, 900))
                elif i >= 2 and i < 5:
                    print("超过2次获取列表页总页码失败, 暂停30~40min重新获取, 重新登录获取!!".format(i))
                    time.sleep(random.uniform(100, 200))
                else:
                    print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                    time.sleep(random.uniform(10, 20))

    def get_page_num(self):
        """
        获取最新搜索数据的最大页码, 与数据库中搜索数据最大页码做比较, 如果前者大于后者说明之前未抓取完成, 将数据库的最大页码作为待抓取的开始抓取页进行抓取,反之, 说明当前年已经抓取完成, 直接进入下一年进行数据抓取
        :param year: 当前列表页所属年份
        :return: 待抓取数据的最大及最小页码
        """
        sql_page_data = self.find_mongo_page()
        # 页码从大到小抓取, 按照增量抓取的逻辑抓取, 由数据库中的最小值与1之间的对比执行一下逻辑, 获取待抓取的最大值与最小值
        # 	1 当数据库中的最小页码值大于1 说明之前没有抓取完, 可以继续抓取
        # 	2 如果数据库中的最小页码值等于1  说明之前已经抓取完成, 需要抓取增量, 这时的最大页码 =  页面最大值 - sql中最大值, 最小值为 0, 倒着抓

        # 	之前共 50 剩20页没抓取
        #
        # 	现在共 80
        #
        # 	最大值计算方式为:  80 - 50 + 20
        # 		新增数据 = 当前页最大值 - sql中最大值
        # 		最大页码 = 新增数据页码 + 之前未抓取完成的数据页码
        # 	做小值计算方式为:  1

        if sql_page_data == 0:
            # total_num, total_page_num = self.request_page_num()
            total_data = self.request_list()
            if total_data == 'no_data':
                return 'no_data'
            total_num, total_page_num = total_data

            print('当前模块数据未抓取过, 从最大页码开始抓取, 最大页为网站总页码: {}, 结束页码为: 0'.format(total_page_num))
            min_page = 0
            max_page = total_page_num
            if total_num == 0:
                self.item.clear()
                print('该模块之前未抓取过, 但本身的项目条数为0, 不抓取!!')
                self.item['phones'] = ''
                self.item['owning_account'] = self.owning_account
                self.item['cur_year'] = self.cur_year
                self.item['cur_page'] = 1
                self.item['type'] = '当前模块数据为空'
                self.save()
                return 'total_zero'
        else:
            sql_min_page = sql_page_data[0][0]
            sql_max_page = sql_page_data[0][1]
            cur_moudle_sql_total = sql_page_data[1]
            print('检测到数据库中最大页码为:{}, 最小页码为: {}'.format(sql_max_page, sql_min_page))
            if int(self.cur_year) >= 2023:
                # 如果为2023年数据,当数据库中存在第一页时需要查看最大页码与网页中最大页码之间的值, 如果有间隔说面有更新
                # total_num, total_page_num = self.request_page_num()
                total_data = self.request_list()
                if total_data == 'no_data':
                    return 'no_data'
                total_num, total_page_num = total_data

                if sql_min_page == 1:
                    print('数据库中最小页码为1,说明之前已经抓取过一遍数据')
                    if sql_max_page < total_page_num:
                        max_page = total_page_num - sql_max_page
                        min_page = 0
                        print('之前已经抓取过全部的一遍数据,目前网站新增数据 {} 页,接下来我们从第 {} 页倒着抓取!!'.format(max_page, max_page))
                    elif total_num - cur_moudle_sql_total > 30:
                        print('当前为第一页数据, 但是页面内项目条数比数据库中存储的数据条数多出 10 条以上,重新抓取第一页数据!!')
                        max_page = 1
                        min_page = 0
                    else:
                        print('网站数据目前还未更新, 或者更新数据不足 {} 条, 不抓取数据!!'.format(self.search_info['page_size']))
                        print('当前模块当前年已经抓取完成, 进入下一模块!!')
                        return 'cur_moudle_have_spider'
                else:
                    print('数据库中最小页码为{}, 大于1 , 说明之前数据还未完全抓取完成, 接下来继续抓取!!'.format(sql_min_page))
                    time.sleep(2)
                    max_page = total_page_num - sql_max_page + sql_min_page
                    min_page = 0
            else:
                if sql_min_page == 1:
                    print('数据库中最小页码为1,说明之前已经抓取过一遍数据')
                    print('当前模块当前模块已经抓取完成, 进入下一模块!!')
                    return 'cur_moudle_have_spider'
                else:
                    total_data = self.request_list()
                    if total_data == 'no_data':
                        return 'no_data'
                    total_num, total_page_num = total_data
                    print('数据库中最小页码为{}, 大于1 , 说明之前数据还未完全抓取完成, 接下来继续抓取!!'.format(sql_min_page))
                    time.sleep(2)
                    # total_num, total_page_num = self.request_page_num()
                    max_page = total_page_num - sql_max_page + sql_min_page
                    min_page = 0
        return min_page, max_page

    def find_mongo_page(self):
        '''
        根据账号和origin_moudle信息锁定待抓取当前年之前已经抓取过保存在数据库中的最大的页面
        :return:
        '''

        sql_page = self.mongo_yii_all.find_yii_page_num(self.origin_moudle)
        print('mongo中获取到的最大 cur_page 为: {}'.format(sql_page))
        return sql_page
    def get_page_list(self):

        list_url = 'http://{}/getCore/manyElements'.format(self.domain)
        header_list = {
            "Host": self.domain,
            "Connection": "keep-alive",
            "Content-Length": "496",
            "Accept": "application/json, text/plain, */*",
            "electronicPublicationStatus": "0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "token": "hzsfdx",
            "Content-Type": "application/json",
            "Origin": "http://{}".format(self.domain),
            "Referer": "http://{}/".format(self.domain),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {
            "pageNo": self.cur_page,
            "pageSize": 50,
            "condition": {
                "main": "",
                "author": "",
                "authorCom": "",
                "periodicalName": "",
                "yearStage": "",
                "yearList": [self.cur_year],
                "journalTypeList": [],
                "sorting": "发表时间",
                "retrieve": " authorCom:*{}* AND pYear:[* TO *] AND start:1 AND !isChMeAss:\"4\" AND !isChMeAss:\"4\" AND start:1 AND !isChMeAss:\"4\" AND start:1 AND !isChMeAss:\"4\" AND start:1 AND !isChMeAss:\"4\" AND start:1".format(
                    self.keywords_)
            }

        }
        print('这是data数据; ',data)
        for i in range(self.retry_down_list_max):
            try:
                time.sleep(random.uniform(2, 5))
                res = self.session.post(list_url, data=json.dumps(data), headers=header_list, timeout=(20, 30))
                res.encoding = 'utf-8'
                if res.status_code == 200 and '请重新进入' not in res.text:
                    list_items = res.json()['list'][0]['resultList']

                    if len(list_items) > 0:
                        for item in list_items:
                            print('***' * 5 + '发现新数据' + '***' * 5)
                            self.item.clear()
                            self.item['art_id'] = item['id']
                            self.item['detail_url'] = 'http://{}/#/details?id={}'.format(self.domain,item['id'])
                            self.item['date'] = item['pubDate'].replace('年', '-').replace('月', '-').replace('日', '')
                            self.item['title'] = item['titleCN']
                            self.item['owning_account'] = self.owning_account
                            self.item['file_name'] = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                                            self.item['title']).replace('fontcolorred', '').replace(
                                'font', '') + '_' + self.item['date'] + '.pdf'
                            # md5_str = self.item['file_name'] + '_' + self.item['date'] + '.pdf'
                            status = self.redis_yii.set_item('yii', self.item['file_name'])
                            if status == 1:
                                self.have_spider_num = 0
                                file_path = self.dir_pdfs + '/' + self.item['file_name']
                                self.item['origin'] = item['periodicalName']
                                self.item['author'] = json.dumps(item['authorList'], ensure_ascii=False)

                                self.item['sitename'] = item['crawlSiteName']
                                self.item['pyear'] = item['pyear']
                                self.item['cur_page'] = self.cur_page
                                self.item['origin_moudle'] = self.origin_moudle
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
                                        print('连续超过 {} 次识别pdf文件失败, 可能遇到了反爬, 等待1~2min, 重新登录一下!!'.format(
                                            self.identify_failed_limit))
                                        time.sleep(random.uniform(60, 120))
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
                                    print('连续抓取过数据超过 {} 个, 向后跳 {} 页, 继续抓取!'.format(self.have_spider_num_max,
                                                                                   self.turn_page_num))
                                    self.cur_page -= self.turn_page_num
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
                print('请求列表页第 {} 次 出现问题, 暂停2~3min, 再次发起请求!!'.format(i))
                time.sleep(random.uniform(120, 180))
                if i >= 2:
                    print('请求列表页第 {} 次 出现问题, 休息5~10分钟,重新登录并发起请求'.format(i))
                    time.sleep(random.uniform(300, 600))
                    self.login_again()

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
            "Referer": "http://{}/".format(self.domain),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        for i in range(self.retry_down_pdf_max):
            print('开始下载pdf文件...')
            try:
                res = self.session.get(url, headers=headers, timeout=(20, 30))
                time.sleep(random.uniform(2, 3))
                if res.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(res.content)
                        f.close()
                    print('pdf文件下载完成!!')
                    self.down_pdffail_num = 0
                    break
                else:
                    print('pdf文件下载失败第 {} 次, url 为 {} 信息为: {}, 等待一下重新下载'.format(i, url, file_path))
                    time.sleep(random.uniform(3, 5))
            except:
                print('下载pdf文件第 {} 次链接读取失败或请求出错,不打紧再来!!'.format(i))
        else:
            print('下载pdf文件连续出错第 {} 次, 休息一下, Go on!!!'.format(self.down_pdffail_num))
            self.down_pdffail_num += 1
            time.sleep(random.uniform(1, 3))
        if self.down_pdffail_num >= 30:
            print('连续 30 个pdf文件下载失败, 可能遇到反爬, 休息2~3分钟后, 向后跳 {} 页, 继续抓取!!'.format(self.turn_page_num))
            time.sleep(random.uniform(120, 180))
            self.login_again()
            # self.cur_page = self.turn_page_num
            # self.down_pdffail_num = 0
            # return 'turn_over'

    def save(self):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        self.item['spider_date'] = spider_date
        if self.item['phones']:
            if len(self.item['phones']) > 1:
                print('注意: 发现当前有 {} 个手机号'.format(len(self.item['phones'])))
                time.sleep(random.uniform(2, 5))
                for phone in self.item['phones']:
                    phones = copy.deepcopy(self.item)
                    phones['phones'] = phone
                    self.mongo_yii_all.insert(phones)
                    # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                    duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf', phone)
                    if duplicate_status == 1:
                        phones['commit_status'] = '未提交'
                        self.mongo_yii_commit.insert(phones)
                        print('发现的手机号已插入 commit 表中!!!')

                    else:
                        print('跳过当前手机号!! 不再放入 commit 表中')
            else:
                self.item['phones'] = self.item['phones'][0]
                self.mongo_yii_all.insert(self.item)
                # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf', self.item['phones'])
                if duplicate_status == 1:
                    self.item['commit_status'] = '未提交'
                    self.mongo_yii_commit.insert(self.item)
                    print('发现的手机号已插入 commit 表中!!!')

                else:
                    print('跳过当前手机号!! 不再放入 commit 表中')
        else:
            print('发现新数据, 但没有手机号, 将手机号重置为空, 放入chaoxing_all中')
            self.item['phones'] = ''
            self.mongo_yii_all.insert(self.item)

    def run(self):
        # print(self.session.cookies)
        for i in range(3):
            try:
                # 排队执行所有待抓取的任务
                for search_info in self.get_search_info():
                    if search_info:
                        self.search_info = search_info
                        print('当前在抓取的任务信息为: ', self.search_info)
                        time.sleep(5)
                        # authorCom:*医*院*
                        self.keywords_ = '*'.join([keyword for keyword in self.search_info['keywords']])
                        print('这是变形后的keywrods: ', self.keywords_)
                        for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):

                            self.cur_year = str(year)
                            self.update_task(self.search_info, have_start=1, is_running=1, cur_year=year)
                            self.origin_moudle = '{}_{}_{}'.format(self.search_info['mode'],
                                                                               self.search_info['keywords'],
                                                                               self.cur_year)
                            self.item['origin_moudle'] = self.origin_moudle

                            print('当前是 {} 年, 基本信息为: {}'.format(self.cur_year, str(self.search_info)))
                            # module_end_year_data = '{}'.format(self.item['origin_moudle'],
                            #                                          self.main_task_info['keywords'], self.cur_year)
                            year_spider_status = self.mongo_yii_all.get_module_end_year(self.origin_moudle)
                            if year_spider_status != 'cur_year_over':
                                data = self.get_page_num()
                                print('get_page_num结果为: {}'.format(str(data)))
                                if data == 'cur_moudle_have_spider':
                                    print('当前模块已经抓取过!! 跳过!!')
                                    continue
                                elif data == 'total_zero':
                                    print('检测到 web 总项目数为 0 , 跳过当前模块')
                                    continue
                                elif data == 'no_data':
                                    print('检测到 当前模块只返回抱歉的一句话, 无数据, 跳过!!')
                                    continue
                                if data:
                                    # 进入新的一年后, 将已经抓去过数据数量设置为 0
                                    min_page, max_page = data
                                    self.cur_page = max_page
                                    while self.cur_page > min_page:
                                        # for page in range(min_page,max_page):
                                        print('当前是{} {} {} {}年 第 {} 页数据'.format(self.owning_account, self.search_info['mode'],
                                                                                self.search_info['keywords'], year,
                                                                                self.cur_page))
                                        spider_status = self.get_page_list()
                                        if spider_status == 'turn_over':
                                            print('检测到当前发生了页面跳过, 跳转之后的页码为: {}'.format(self.cur_page))
                                            time.sleep(random.uniform(2, 5))
                                        self.cur_page -= 1
                                else:
                                    print('开始抓取下一年数据!')
                            else:
                                print('当前年已经抓取过, 不再继续抓取!!')
                            self.mongo_yii_all.insert_module_end_year(self.origin_moudle)
                        self.update_task(self.search_info, have_end=1, is_running=0, cur_year=self.cur_year)
                    else:
                        print('发现任务无法再次运行,跳过!!开始进行下一任务!!')
                break
            except Exception as e:
                print('抓取时出现问题, 休息10~15分钟, 详情为: {}'.format(repr(e)))
                time.sleep(random.uniform(600, 900))
