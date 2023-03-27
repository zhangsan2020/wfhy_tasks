# -*- coding:utf-8 -*-
import copy
import json
import os
import random
import re
from datetime import datetime
from urllib.parse import urljoin

from lxml import etree
import ddddocr
import requests
import time
from requests.adapters import HTTPAdapter
from task.zhiwang.zw_common import user_info, headers_list, min_limit
from task.common.cur_identify import CurIdentify
from task.SqlSave.mongo_store import MongoStore
from task.zhiwang.redis_zw import ZwRedis
from task.common.log import FrameLog
from task.common.useragent import useragent_pool


class ZwSpider():

    def __init__(self):

        # self.year = '2018'
        self.max_year = 2019
        self.min_year = 2018
        self.headers_init = {
            'User-Agent': random.choice(useragent_pool)
        }
        # self.zw_cookie = ZwCookie()
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.ori_jsondata_url = './task/zhiwang/moudle_data/old_篇名_手术_年_学科_主题.json'
        self.list_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
        self.userinfo = user_info
        self.headers_list = headers_list
        # self.searchinfo = {'model': '作者单位', 'keywords': '医药'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '病例'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '感染'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '肿瘤'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '细胞'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '基因'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '关节'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '术后'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '病毒'}
        # self.searchinfo = {'model': '参考文献', 'keywords': '疗'}
        self.searchinfo = {'model': '篇名', 'keywords': '手术'}
        # self.searchinfo = {'model': '篇名', 'keywords': '细胞'}

        self.dir_pdfs = 'E:/zhiwang_pdfs/'  # 末尾一定要加上 / , 否则将会自动使用\做填充, 路径会出现问题
        self.identify = CurIdentify()
        self.mongo_zw_all = MongoStore('wfhy_update', 'zw_all')
        self.mongo_zw_commit = MongoStore('wfhy_commit', 'zw_commit')
        self.redis_zw = ZwRedis()
        self.redis_all_phones = ZwRedis()
        self.log = FrameLog('zw_cnki').get_log()
        self.retry_getsearchsql = 1
        self.HandlerId = 0
        self.page_items_retry = 0
        # 连续第多少次重新下载, 如果检测到列表页面中detail与pdf连续10次之前被下载过, 将不再对当前模块发起请求, 直接接入下一模块
        self.havedown_times = 1
        # self.years = ['2022','2021','2020','2019']
        self.pdfdown_fail = 0
        self.pay_permission = 0
        self.havepdfdown = 0
        self.item = {}

    def update_task(self, condition, **kwargs):

        platform = condition['platform']
        keywords = condition['keywords']
        max_year = condition['max_year']
        min_year = condition['min_year']
        with open(self.tasks_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for index, search_info in enumerate(json_data):
            # print('这是要看的search_info: ',search_info)
            if search_info['owning_account'] == self.owning_account and search_info['platform'] == platform and \
                    search_info['keywords'] == keywords and search_info[
                'max_year'] == max_year and search_info['min_year'] == min_year:
                print(platform, keywords, kwargs)
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
            if base_info['owning_account'] == self.owning_account and base_info['have_end'] != 1 and base_info[
                'is_running'] != 1 and base_info['spider_at'] == self.spider_at:
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
        self.session = self.login_obj.login_page_turn(self.owning_account)

    def get_page_num(self):
        '''
        获取最新搜索数据的最大页码, 与数据库中搜索数据最大页码做比较, 如果前者大于后者说明之前未抓取完成, 将数据库的最大页码作为待抓取的开始抓取页进行抓取,反之, 说明当前年已经抓取完成, 直接进入下一年进行数据抓取
        :param year: 当前列表页所属年份
        :return: 待抓取数据的最大及最小页码
        '''
        list_url = 'http://www-sinomed-ac-cn.njmu.jitui.me/zh/basicSearch.do?sf_request_type=ajax'

        data = {
            "sql": "AD_ALL/1='{}' AND DP_YEAR/1='{}'".format(self.search_info['keywords'], self.cur_year),
            "dbtype": "zh",
            "pageNo": "1",
            "pageSize": self.search_info['page_size'],
            "ajax": "items",
            "searchword": "(\"{}\"[{}]) AND (\"{}\"[时间]) ".format(self.search_info['keywords'],
                                                                  self.search_info['platform'], self.cur_year),
            "cmode": "tl",
            "orderBy": "LIFO",
            "flag": "true",
            "selected": "undefined"
        }
        header_list = {
            # "Host": "www-sinomed-ac-cn.njmu.jitui.me",
            "Connection": "keep-alive",
            "Content-Length": "288",
            "Accept": "text/html, */*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "http://www-sinomed-ac-cn.njmu.jitui.me",
            "Referer": "http://www-sinomed-ac-cn.njmu.jitui.me/zh/basicSearch.do?searchwordwm={}{}".format(
                quote(self.search_info['keywords']), quote(self.search_info['platform'])),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        for i in range(self.retry_down_list_max):
            # try:
            time.sleep(random.uniform(2, 5))
            try:
                res = self.session.post(list_url, data=data, headers=header_list, timeout=(20, 30))
            except Exception as e:
                print('请求获取get_page_num时出现错误: {}!!'.format(repr(e)))
                time.sleep(random.uniform(2,5))
                if i >= 2:
                    print('获取 最大页码时 连续超过2次出错, 重新登录获取数据!!!')
                    self.login_again()
                continue
            res.encoding = 'utf-8'
            max_page_data = re.findall('共(\d+)页&nbsp;', res.text)
            if res.status_code == 200 and max_page_data:
                new_page_num = int(max_page_data[0])
                total = new_page_num * self.search_info['page_size']
                print('当前模块含有文章 {} 页, 预估共 {} 条'.format(new_page_num, total))
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
                    print('当前年数据未抓取过, 从最大页码开始抓取, 最大页为网站总页码: {}, 结束页码为: 0'.format(new_page_num))
                    min_page = 0
                    max_page = new_page_num
                else:
                    sql_min_page = sql_page_data[0]
                    sql_max_page = sql_page_data[1]
                    print('检测到数据库中最大页码为:{}, 最小页码为: {}, 网站最大页码为: {}'.format(sql_max_page, sql_min_page, new_page_num))
                    if sql_min_page == 1:
                        print('数据库中最小页码为1,说明之前已经抓取过一遍数据')
                        if sql_max_page < new_page_num:
                            max_page = new_page_num - sql_max_page
                            min_page = 0
                            print('之前已经抓取过全部的一遍数据,目前网站新增数据 {} 页,接下来我们从第 {} 页倒着抓取!!'.format(max_page, max_page))
                        else:
                            print('网站数据目前还未更新, 或者更新数据不足 {} 条, 不抓取数据!!'.format(self.search_info['page_size']))
                            print('当前模块当前年已经抓取完成, 进入下一年')
                            return 'cur_year_have_spider'
                    else:
                        print('数据库中最小页码为{}, 大于1 , 说明之前数据还未完全抓取完成, 接下来继续抓取!!'.format(sql_min_page))
                        time.sleep(2)
                        max_page = new_page_num - sql_max_page + sql_min_page
                        min_page = 0
                return min_page, max_page

            elif res.status_code == 200 and '登录失效' in res.text:
                print('当前页面出现登录失效, 休息3~5min, 重新登录后继续获取!!')
                time.sleep(random.uniform(180, 300))
                self.login_again()
            elif res.status_code == 200 and '找不到和您的查询相符的资源' in res.text:
                print('检索关键字有问题, 没有查到相关的资源, 退出!!')
                exit()
            else:
                if i >= 5:
                    print("超过5次获取列表页总页码失败, 暂停30~40min重新获取, 重新登录获取!!".format(i))
                    self.login_again()
                    time.sleep(random.uniform(1800, 2400))
                elif i >=2 and i< 5:
                    print("超过5次获取列表页总页码失败, 暂停30~40min重新获取, 重新登录获取!!".format(i))
                    self.login_again()
                    time.sleep(random.uniform(300, 600))
                else:
                    print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                    time.sleep(random.uniform(10, 20))

    def find_mongo_page(self):
        '''
        根据账号和origin_moudle信息锁定待抓取当前年之前已经抓取过保存在数据库中的最大的页面
        :return:
        '''

        sql_page = self.sw_mongo_all.find_page_num(self.owning_account, self.item['origin_moudle'])
        return sql_page

    def get_userinfo(self):

        userinfo = random.choice(self.userinfo)
        return userinfo

    def get_checkcode(self, img):

        ocr = ddddocr.DdddOcr(old=True)
        # 第一个验证截图保存：verification_code_1.png
        with open(img, 'rb') as f:
            image = f.read()
        try:
            res = ocr.classification(image)
        except:
            res = ''
        return res

    def login(self):

        user_agent = random.choice(useragent_pool)
        self.headers_init['User-Agent'] = user_agent
        # self.log.info('开始登录,请稍等...')
        time.sleep(1)
        userinfo = self.get_userinfo()
        print('当前用户信息为: ', userinfo)
        # self.log.info('当前用户信息为: {}'.format(userinfo))
        username = userinfo['username']
        password = userinfo['password']
        img_retry = 1
        imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
        # self.log.info('请求并识别验证码!!')
        for i in range(10):
            print('尝试是第 {} 次发起登录请求!!'.format(i))
            res = self.session.get(imgcode_url, headers=self.headers_init, timeout=(10, 20))
            with open('imgcode.jpg', 'wb') as f:
                f.write(res.content)
                f.close()
            code_str = self.get_checkcode('imgcode.jpg')
            print('验证码字符串为: ', code_str)
            # self.log.info('验证码识别结果为: {}'.format(code_str))
            time_ = int(time.time() * 1000)
            url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&checkCode={}&p=0&_={}'.format(
                username, password, code_str, time_)
            res = self.session.get(url, headers=self.headers_init, timeout=(10, 20))
            if '验证码不正确' in res.text:
                print('验证码识别出错, 正在重新识别, 请稍后!!!')
                time.sleep(2)

            elif '登录失败，没有该用户' in res.text:
                print('账号密码出现问题, 请确认账号密码!')

            elif '登录成功' in res.text:
                print('登录成功!!')
                break

            else:
                print('登录请求返回数据为: ',res.text)
                print('休息一下1分钟, 重新发起请求')
                time.sleep(60)

    def get_searchsql(self):

        url = 'https://kns.cnki.net/kns8/defaultresult/index'

        for i in range(5):
            try:
                print('清理session中的cookies')
                self.session.cookies.clear()
                self.login()
                self.session.get(url, headers=self.headers_init, timeout=(15, 20))
                time.sleep(random.uniform(0, 0.5))

                cookie_dblang = {
                    "dblang": "ch"
                }
                self.session.cookies.update(cookie_dblang)
                # 获取大的搜索模块基本数据
                header_field = {
                    'Referer': 'https://www.cnki.net/',
                    'User-Agent': random.choice(useragent_pool)
                }
                field_json_url = 'https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6'
                res = self.session.get(field_json_url, headers=header_field)
                self.searchinfo['model_match_data'] = \
                re.findall(r'Text:"' + self.searchinfo['model'] + '",Value:"(\w+).*?"}', res.text)[0]
                self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + \
                                 self.searchinfo['model'] + '","Name":"' + self.searchinfo[
                                     'model_match_data'] + '","Value":"' + self.searchinfo[
                                     'keywords'] + '","Operate":"%"}],"ChildItems":[]}]}}'
                # 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

                # 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数
                status = self.request_searchsql()
                if status == "temp_code_ok":
                    print('临时验证码验证成功,等待10到20分钟,重新执行 get_searchsql')
                    time.sleep(random.uniform(300, 900))
                else:
                    print('reqeust_searchsql 返回结果为: {}'.format(status))
                break

            except:
                print('第 {} 次请求列表首页出现问题, 等待2分钟后重新发起请求!!!'.format(i))
                time.sleep(120)
                if i == 2:
                    print('第2次请求列表首页出现问题, 等待半小时后重新发起请求!!!')
                    time.sleep(1800)
                # self.session.get(url, headers=self.headers_init, timeout=(5, 20))



    def request_searchsql(self):

        data = {
            'IsSearch': 'true',
            'QueryJson': self.queryjson,
            'PageName': 'defaultresult',
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
            'CurPage': 1,
            'RecordsCntPerPage': 20,
            'CurDisplayMode': 'listmode',
            'CurrSortField': 'PT',
            'CurrSortFieldType': 'desc',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }
        self.headers_list['User-Agent'] = random.choice(useragent_pool)
        for i in range(5):
            try:
                res = self.session.post(self.list_url, data=data, headers=self.headers_list, timeout=(10, 20))
                time.sleep(random.uniform(0, 0.5))
                print('这是请求的状态码: {}'.format(res.status_code))
                if res.status_code == 200 and ('题名' in res.text and '发表时间' in res.text):
                    html = etree.HTML(res.text)
                    searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
                    if searchsql_data:
                        searchsql = searchsql_data[0]
                        self.searchsql = searchsql
                        self.retry_getsearchsql = 0
                        break
                    else:
                        print('未获取到sqlval, 暂停5秒, 重新请求!!')
                        time.sleep(random.uniform(30,60))

                elif res.status_code == 200 and '请输入验证码' in res.text:
                    print('出现了验证码, 开始识别!')
                    self.log.warning('出现了验证码, 开始识别!')
                    for i in range(10):
                        status = self.check_code()
                        if status == 1:
                            return "temp_code_ok"
                        else:
                            print('临时验证码第 {} 次识别出现问题,重新识别'.format(i))

                else:
                    print('出现了其它异常!!! 休息一会儿再次发起请求!!')
                    time.sleep(random.uniform(30,60))
            except:
                print('第 {} 次请求列表首页请求或读取超时!!!'.format(i))
                if i >= 2:
                    print('请求列表页数据第 {} 次出现问题, 等待半小时后重新发起请求!'.format(i))
                    time.sleep(1800)
                # res = self.session.post(self.list_url, data=data, headers=self.headers_list, timeout=(5, 20))


    def check_code(self):

        code_url = 'https://kns.cnki.net/kns8/Brief/VerifyCode?t=82283164-b460-420d-9f91-3e402f5714b8&orgin=OverMaxSearchCount'
        res = self.session.get(code_url)
        with open('zw_temp_code.jpg', 'wb') as f:
            f.write(res.content)
            f.close()
        code = self.get_checkcode('./zw_temp_code.jpg')
        print(code)
        check_url = 'https://kns.cnki.net/kns8/Brief/CheckCode'
        data = {
            'vericode': code,
            'corgin': 'OverMaxSearchCount'
        }
        headers = {
            "Host": "kns.cnki.net",
            "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }

        res = self.session.post(check_url, data=data, headers=headers)
        print('这是出现临时验证码后的验证结果: ',res.text)
        if '参数错误' in res.text:
            print('临时验证码识别时, 参数错误!!')
        else:
            print('临时验证码验证成功')
            return 1
    def get_page_items(self, page_num, subject_info, title_info):

        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + \
                         self.searchinfo['model'] + '","Name":"' + self.searchinfo['model_match_data'] + '","Value":"' + \
                         self.searchinfo[
                             'keywords'] + '","Operate":"%"}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"1","Title":"","Logic":1,"Items":[{"Key":"' + \
                         title_info['title_text'] + '","Title":"' + title_info['title_text'] + '","Logic":2,"Name":"' + \
                         title_info['title_type'] + '","Operate":"","Value":"' + title_info[
                             'title_text'] + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"' + \
                         subject_info['value'] + '?","Title":"' + subject_info[
                             'subject_name'] + '","Logic":2,"Name":"' + subject_info[
                             'field'] + '","Operate":"","Value":"' + subject_info[
                             'value'] + '?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + self.cur_year + '","Title":"' + self.cur_year + '","Logic":2,"Name":"年","Operate":"","Value":"' + self.cur_year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]}}'
        params = {
            'IsSearch': 'true',
            'QueryJson': self.queryjson,
            'SearchSql': self.searchsql,
            'PageName': 'defaultresult',
            'HandlerId': self.HandlerId,
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN',
            'CurPage': page_num,
            'RecordsCntPerPage': 20,
            'CurDisplayMode': 'listmode',
            'CurrSortField': 'PT',
            'CurrSortFieldType': 'desc',
            'IsSortSearch': 'false',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }

        if page_num > 1:
            params['IsSearch'] = 'false'

        print('*' * 20)
        print('这是要看的params: {}'.format(str(params)))
        print('*' * 20)
        for i in range(5):
            self.headers_list['User-Agent'] = random.choice(useragent_pool)
            # 第二次获取根据日期排序的列表数据, 以下可改变页码来获取数据
            try:
                res = self.session.post(self.list_url, data=params, headers=self.headers_list, timeout=(10, 20))
                time.sleep(random.uniform(0,0.3))
            except:
                print('列表页第 {} 次请求超时或读取失败, 休息一下, 重新登录并获取列表页数据!!')
                time.sleep(random.uniform(20,30))
                self.get_searchsql()
                continue
            if res.status_code == 200 and ('题名' in res.text and '发表时间' in res.text):
                html = etree.HTML(res.text)
                self.HandlerId = html.xpath('//input[@id="HandlerIdHid"]/@value')[0]
                trs = html.xpath('//table[@class="result-table-list"][1]//tr')[1:]
                page_items = []
                for tr in trs:
                    item = {}
                    if tr.xpath('./td[@class="name"]/a/@href'):
                        base_source_link = 'https://kns.cnki.net'
                        try:
                            a = tr.xpath('./td[@class="name"]/a')[0]
                            item['title'] = a.xpath('string(.)').strip()
                        except:
                            item['title'] = ''
                        try:
                            item['detail_url'] = urljoin(base_source_link, tr.xpath('./td[@class="name"]/a/@href')[0].strip())
                        except:
                            item['detail_url'] = ''
                        try:
                            item['author'] = tr.xpath('./td[@class="author"]')[0].xpath('string(.)').strip()
                        except:
                            item['author'] = ''
                        try:
                            item['source_name'] = tr.xpath('./td[@class="source"]/a/text()')[0].strip()
                        except:
                            item['source_name'] = ''
                        try:
                            item['source_link'] = urljoin(base_source_link,tr.xpath('./td[@class="source"]/a/@href')[0].strip())
                        except:
                            item['source_link'] = ''
                        item['date'] = tr.xpath('./td[@class="date"]/text()')[0].strip()
                        item['source_type'] = tr.xpath('./td[@class="data"]/text()')[0].strip()
                        if tr.xpath('./td[@class="download"]/a/text()'):
                            item['down_num'] = tr.xpath('./td[@class="download"]/a/text()')[0].strip()
                        else:
                            item['down_num'] = 0
                    else:
                        print('详情页链接地址为空!!')
                    page_items.append(item)
                return page_items
            else:
                print('第 {} 次没有获取到当前列表页的数据,稍等5~10分钟, 接下来重新登录重新获取当前页面的数据'.format(i))
                # self.log.info('没有获取到当前列表页的数据,接下来重新登录重新获取当前页面的数据')
                time.sleep(random.uniform(300, 600))
                self.get_searchsql()


    def get_page_list(self):
        # years = choice_moudle['years'][]
        # for year in years:
        with open(self.ori_jsondata_url, 'r', encoding='utf-8') as f:
            data = f.read()
        json_data = json.loads(data)
        self.get_searchsql()
        for year in range(self.max_year,self.min_year,-1):
            self.cur_year = str(year)
            moudle_datas = json_data[self.cur_year]
            for index,moudle_data in enumerate(moudle_datas):

                subject_info = moudle_data['subject_info']
                for title_info in moudle_data['title_info'].values():
                    little_key = title_info['title_type'] + '__' + title_info['title_text']
                    print('当前是{},{}, {} 年, 学科为: {}, 标题为: {}'.format(self.searchinfo['model'],self.searchinfo['keywords'],year, str(subject_info['subject_name']),little_key))
                    time.sleep(2)
                    for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):
                        self.cur_year = year
                        self.update_task(self.search_info, have_start=1, is_running=1, cur_year=self.cur_year)
                        self.item['origin_moudle'] = '{}_{}_{}年'.format(self.search_info['platform'],
                                                                           self.search_info['keywords'],
                                                                           self.cur_year)
                        print('当前是 {} 年, 基本信息为: {}'.format(self.cur_year, str(self.search_info)))

                        data = self.get_page_num()
                        if data != 'cur_year_have_spider':
                            # 进入新的一年后, 将已经抓去过数据数量设置为 0
                            min_page, max_page = data
                            self.cur_page = max_page
                            while self.cur_page > min_page:
                                # for page in range(min_page,max_page):
                                print(
                                    '当前是{} {} {} {}年 第 {} 页数据'.format(self.owning_account, self.search_info['platform'],
                                                                      self.search_info['keywords'], year,
                                                                      self.cur_page))
                                spider_status = self.get_page_list()
                                if spider_status == 'turn_over':
                                    print('检测到当前发生了页面跳过, 跳转之后的页码为: {}'.format(self.cur_page))
                                    time.sleep(random.uniform(2, 5))
                                self.cur_page -= 1
                        else:
                            print('开始抓取下一年数据!')
                    self.update_task(self.search_info, have_end=1, is_running=0, cur_year=self.cur_year)

                    # if not 'have_spider' in json_data[self.cur_year][index]['title_info'][little_key]:
                    #     print('当前模块未被抓去过, 可放心大胆去抓取!!!')
                    #     time.sleep(2)
                    #     for page_num in range(1, 301):
                    #         print('***' * 20)
                    #         print('当前是 {} 年, 学科为: {}, 标题为: {} 中的第 {} 页数据'.format(year, str(subject_info['subject_name']),
                    #                                                              little_key, page_num))
                    #         print('***' * 20)
                    #         # self.log.info('当前是 {} 年, 学科为: {}, 研究层次为: {} 中的第 {} 页数据'.format(year,str(subject_info),str(study_info),page_num))
                    #         time.sleep(random.uniform(1, 4))
                    #         page_items = self.get_page_items(page_num, subject_info, title_info)
                    #         # print('这是要看的items数据: ',page_items)
                    #         if page_items:
                    #             status = self.download_detail_pdf(page_items)
                    #             if status == 0:
                    #                 print('列表页连续超过10条详情及pdf数据之前被下载过, 说明当前模块之后的数据都已被下载过, 不再继续请求')
                    #                 # self.log.info('列表页连续超过10条详情及pdf数据之前被下载过, 说明当前模块之后的数据都已被下载过, 不再继续请求')
                    #                 break
                    #         else:
                    #             print('当前搜索没有数据了, 开始进行新的搜索模块!!')
                    #             time.sleep(1)
                    #             break
                    #     print('开始进入下一模块...., 请稍后!!')
                    #     time.sleep(3)
                    #     spider_date = datetime.now().strftime('%Y%m%d%H%M')
                    #     json_data[year][index]['title_info'][little_key]['have_spider'] = spider_date
                    #     new_data = json.dumps(json_data,ensure_ascii=False)
                    #     with open(self.ori_jsondata_url,'w',encoding='utf-8') as f:
                    #         f.write(new_data)
                    #         f.close()
                    #     print('开始进入下一模块...., 请稍后!!')
                    # else:
                    #     print('{} 模块已经抓去过, 开始进入下一模块.'.format(little_key))
                    #     time.sleep(2)

    def parse_detail_html(self, html):

        detail_html = etree.HTML(html)
        pdf_url_data = detail_html.xpath('//a[@id="pdfDown"]/@href')[0]
        base_url = 'https://bar.cnki.net'
        pdf_url = urljoin(base_url, pdf_url_data)
        return pdf_url

    def download_detail_pdf(self, page_item_data):

        # print('这是要看的数据 page_item_data:  ', page_item_data)
        headers_detail = {
                # "Host": "kns.cnki.net",
                "Connection": "keep-alive",
                "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                # "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-User": "?1",
                "Sec-Fetch-Dest": "document",
                "Referer": "https://kns.cnki.net/kns8/defaultresult/index",
                # "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
        if self.pdfdown_fail > 4:
            print('连续4次发现pdf文件大小不到50k,稍等一下, 重新登录并获取searchsql!!!')
            time.sleep(random.uniform(180,400))
            self.get_searchsql()
            self.pdfdown_fail = 0

        for item in page_item_data:
            # 1代表请求成功
            self.item.clear()
            name = '{}_{}.pdf'.format(item['title'].replace('/', '_'), item['date'].replace(' ', '&'))
            # print('name等于: ', name)
            file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", name)
            self.item['file_name'] = file_name
            duplicate_status = self.redis_zw.set_item('zw_cnki', file_name)
            time.sleep(random.uniform(0.1,0.3))
            if duplicate_status == 1:
                self.havedown_times = 0
                print('是否请求状态为: {}, 之前未请求过, 即将发起请求'.format(duplicate_status))
                detail_url = self.item['detail_url']
                for i in range(4):
                    try:
                        res = self.session.get(detail_url, headers=headers_detail, timeout=(10, 20))
                        time.sleep(random.uniform(0.1,0.4))
                        if res.status_code == 200 and ('分页下载' not in res.text) and 'pdfDown' in res.text:
                            self.havepdfdown = 0
                            print('detail_url 为: ', self.item['detail_url'])
                            print('detail_url_302为: ', res.url)
                            self.item['detail_url'] = res.url
                            detail_html = etree.HTML(res.text)
                            pdf_url = detail_html.xpath('//a[@id="pdfDown"][1]/@href')[0]
                            if 'javascript' not in pdf_url:
                                base_url = 'https://bar.cnki.net'
                                self.item['pdf_url'] = urljoin(base_url, pdf_url)
                                print('开始下载pdf文件......')
                                self.download_pdf()
                                time.sleep(random.uniform(0, 1))
                                self.save()
                            else:
                                print('详情链接中含有javascript, 应该是需要充钱付费的, 请查看, pdf链接地址为: {}'.format(pdf_url))
                            break
                        elif 'CAJ原文下载' in res.text or '分页下载' in res.text:
                            print('当前为 CAJ原文下载, 跳过!! 连接地址为: {}'.format(res.url))
                            time.sleep(random.uniform(0.2, 0.5))
                            break
                        elif 'pdfDown' not in res.text:
                            print('当前页面不含有pdf下载按钮,详情页链接地址为: {}'.format(detail_url))
                            break
                        else:
                            print('详情页链接地址请求有问题, 状态不为200 或者其它特殊情况, 请详细查看,详情页链接地址为: {}'.format(detail_url))
                            if i >= 2:
                                print('请求页请求连续超过2次, 重新登录之后再次获取!!')
                                self.login()
                                time.sleep(random.uniform(2, 3))
                                self.get_searchsql()
                            # self.havepdfdown += 1
                            # print('当前状态码为: {}'.format(res.status_code))
                            # print('连续第 {} 次获取详情页连接地址出现问题, 状态不为200 或者页面内不含有pdfdown! 放慢下速度... url地址为: {}'.format(
                            #     self.havepdfdown,
                            #     res.url))
                            # time.sleep(random.uniform(60, 100))
                            # # self.get_searchsql()
                            # if self.havepdfdown > 2:
                            #     print('连续超过3 次获取详情页连接地址出现问题, 暂停3~5分钟, 重新登录获取!')
                            #     time.sleep(random.uniform(180, 300))
                            #     self.get_searchsql()
                            #     self.havepdfdown = 0

                    except:
                        print('请求详情页第 {} 次出现问题, 休息一下再次请求!!'.format(i))
                        time.sleep(random.uniform(5,10))
                        if i >= 2:
                            print('请求页请求连续超过2次, 重新登录之后再次获取!!')
                            self.login()
                            time.sleep(random.uniform(2,3))
                            self.get_searchsql()

            else:
                print('当前详情页以及pdf文件都已经下载过, 不再继续做处理!!!')
                self.havedown_times += 1
                if self.havedown_times <= 154:
                    print('列表页中发现第 {} 次之前连续被下载过的痕迹'.format(self.havedown_times))
                    # self.log.info('列表页中发现第 {} 次之前连续被下载过的痕迹'.format(self.havedown_times))
                    time.sleep(random.uniform(0.1,0.5))
                else:
                    print('发现连续之前被下载过的详情及pdf痕迹超过 {} 条,不再下载, 跳过本模块'.format(self.havedown_times))
                    self.havedown_times = 0
                    return 0
        return 1

    def download_pdf(self):

        headers_pdf = {
            # "Host": "bar.cnki.net",
            "Connection": "keep-alive",
            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": self.item['detail_url'],
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        for i in range(5):
            try:
                # item['pdf_url'] = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&dbname=CJFDZHYX&filename=SZBB201808019&uniplatform=NZKPT&v=-VcQfQ2UntzmsOPlJT8_o7bI5XxaP3WR9xxFFoXzmHpGLpvvY9P9FSDkN_ddbncL'
                res = self.session.get(self.item['pdf_url'], headers=headers_pdf, timeout=(10, 20))
                time.sleep(random.uniform(0, 0.5))
                if res.headers.get('Content-Length'):
                    if res.status_code == 200 and ('本篇支付' not in res.text) and int(
                            res.headers['Content-Length']) > min_limit:
                        self.pdfdown_fail = 0
                        self.pay_permission = 0
                        self.item['need_pay'] = '无需支付'
                        file_path = os.path.join(self.dir_pdfs, self.item['file_name'])
                        pdf_obj = open(file_path, 'wb')
                        pdf_obj.write(res.content)
                        pdf_obj.close()
                        print('下载路径地址为: {}'.format(file_path))
                        print('开始识别医生信息...')
                        doctor_infos = self.identify.identify_pdf(file_path)
                        print('识别结果为: ', doctor_infos)
                        self.item.update(doctor_infos)
                        print("添加医生信息后的数据为: ", self.item)
                        break

                    elif ('本篇支付' in res.text) or ('没有订购此产品' in res.text) or ('没有此产品的使用权限' in res.text):
                        self.pay_permission += 1
                        print('检测到连续含有本篇支付或者无权限pdf文件第 {} 次,标题为: {}'.format(self.pay_permission, self.item['title']))
                        time.sleep(random.uniform(2, 5))
                        if self.pay_permission > 8:
                            print('检测到连续含有本篇支付或者无权限pdf文件超过6次, 暂停3min, 重新登录获取文件数据!!')
                            time.sleep(180)
                            self.get_searchsql()
                            self.pay_permission = 0
                        # print('检测到含有本篇支付或者无使用权限存在, 标题为: ', item['title'])
                        self.item['need_pay'] = '需支付/无访问权限'
                        self.item['doctor_info'] = ''
                        self.item['phones'] = ''
                        self.item['identify_status'] = '未识别'
                        break

                    elif int(res.headers['Content-Length']) < min_limit:

                        self.pay_permission = 0
                        self.pdfdown_fail += 1
                        print('注意!!当前的pdf文件下载第 {} 次小于 50 k, 重新下载, 当前pdfdown_fail的值为: {}'.format(i,self.pdfdown_fail))
                        time.sleep(random.uniform(5, 10))
                        if i > 1:
                            print('下载小于50k超过2次, 重新登录并下载')
                            self.get_searchsql()
                        self.item['doctor_info'] = ''
                        self.item['phones'] = ''
                        self.item['identify_status'] = '文件过小未下载'

                    else:
                        self.pay_permission = 0
                        print('出现了其它问题, 请注意!!')
                        break
                # print(dir(res.history))
                # print('这是pdf_url: {} ,这是res.hietory属性'.format(item['pdf_url'],dir(res.history)))
            except Exception as e:
                print('pdf文件第 {} 次下载出现异常, 继续下载, 信息为: {}'.format(i,repr(e)))


    def save(self):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        self.item['spider_date'] = spider_date
        if self.item['phones']:
            if len(self.item['phones']) > 1:
                print('注意: 发现当前有 {} 个手机号'.format(len(self.item['phones'])))
                time.sleep(random.uniform(2,5))
                for phone in self.item['phones']:
                    phones = copy.deepcopy(self.item)
                    phones['phones'] = phone
                    self.mongo_zw_all.insert(phones)
                    # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                    duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf',phone)
                    if duplicate_status == 1:
                        phones['commit_status'] = '未提交'
                        self.mongo_zw_commit.insert(phones)
                        print('发现的手机号已插入 commit 表中!!!')
                    else:
                        print('跳过当前手机号!! 不再放入 commit 表中')
            else:
                self.item['phones'] = self.item['phones'][0]
                self.mongo_zw_all.insert(self.item)
                # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf', self.item['phones'])
                if duplicate_status == 1:
                    self.item['commit_status'] = '未提交'
                    self.mongo_zw_commit.insert(self.item)
                    print('发现的手机号已插入 commit 表中!!!')

                else:
                    print('跳过当前手机号!! 不再放入 commit 表中')
        else:
            print('发现新数据, 但没有手机号, 将手机号重置为空, 放入sw_mongo_all中')
            self.item['phones'] = ''
            self.mongo_zw_all.insert(self.item)
        self.item.clear()

    def run(self):

        # (首先获取列表页session, 接着登录, 接着获取列表页获取searchsql数据)(放到一起,生成session,当cookie过期时,可重复更新获取), 接着重复遍历列表页数据, 接着根据详情页链接获取pdf数据进行保存
        # page_items = self.get_page_list()
        # for page_item_data in page_items:
        #     self.download_detail_pdf(page_item_data)
        self.get_page_list()
        # try:
        #     self.get_page_list()
        # except:
        #     time.sleep(1800)
        #     self.get_page_list()
# 新增时的思路是: 获取数据库最大的日期与对应的title,锁定到具体在第几页, 然后倒着去获取数据
# queryjson里面的name决定了大块的搜索范围, 如: 参考文献: 临床医学: RF  作者单位: 医院: AF, 可以请求 https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6获取对应的json标记
