# -*- coding:utf-8 -*-
import copy
import json
import os
import random
import re
from datetime import datetime
from urllib.parse import urljoin

import ddddocr
from lxml import etree
import time
from task.zhiwang.zw_common import user_info, headers_list, min_limit
from task.common.cur_identify import CurIdentify
from ..zw_mongo import ZwMongo
from task.zhiwang.redis_zw import ZwRedis
# from task.common.log import FrameLog
from task.common.useragent import useragent_pool
from ..zw_login import ZwLogin

class ZwSpider():

    def __init__(self):

        self.owning_account = '无'
        self.platform = '篇名'
        self.headers_init = {
            'User-Agent': random.choice(useragent_pool)
        }
        self.zwlogin = ZwLogin()
        self.session = None
        self.module_dir = '篇名_年_学科_主题'
        # 主目录
        self.main_task_path = './task/zhiwang/module_data/zw_tasks_config.json'
        # 子目录
        self.task_sub_dir = './task/zhiwang/module_data/{}'.format(self.module_dir)
        self.dir_pdfs = 'E:/zhiwang_pdfs/'  # 末尾一定要加上 / , 否则将会自动使用\做填充, 路径会出现问题
        self.identify = CurIdentify()
        self.list_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
        self.userinfo = user_info
        self.headers_list = headers_list
        # self.main_task_info = {'model': '作者单位', 'keywords': '医药'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '病例'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '感染'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '肿瘤'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '细胞'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '基因'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '关节'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '术后'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '病毒'}
        # self.main_task_info = {'model': '参考文献', 'keywords': '疗'}
        # self.main_task_info = {'model': '篇名', 'keywords': '手术'}
        # self.main_task_info = {'model': '篇名', 'keywords': '细胞'}
        self.mongo_zw_all = ZwMongo('wfhy_update', 'zw_all')
        self.mongo_zw_commit = ZwMongo('wfhy_commit', 'zw_commit')
        self.redis_zw = ZwRedis()
        self.redis_all_phones = ZwRedis()
        # self.log = FrameLog('zw_cnki').get_log()
        self.retry_getsearchsql = 1
        self.HandlerId = 0
        self.page_items_retry = 0
        # 连续第多少次重新下载, 如果检测到列表页面中detail与pdf连续10次之前被下载过, 将不再对当前模块发起请求, 直接接入下一模块
        # self.years = ['2022','2021','2020','2019']
        self.pdfdown_fail = 0
        self.pay_permission = 0
        self.item = {}
        self.retry_down_pdf_max = 5
        self.retry_down_list_max = 10
        self.have_spider_num = 0
        self.have_spider_num_max = 157
        self.turn_page_num = 2
        self.identify_failed = 0
        self.identify_failed_limit = 52
        self.get_pdf_url_failed = 0
        self.max_task_mum = 2

    def update_task(self, condition, **kwargs):

        platform = condition['platform']
        keywords = condition['keywords']
        max_year = condition['max_year']
        min_year = condition['min_year']
        with open(self.main_task_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for index, search_info in enumerate(json_data):
            # print('这是要看的search_info: ',search_info)
            if search_info['platform'] == platform and \
                    search_info['keywords'] == keywords and search_info[
                'max_year'] == max_year and search_info['min_year'] == min_year:
                print(platform, keywords, kwargs)
                json_data[index].update(kwargs)
                print('这是更新后的json_data!!!')
        with open(self.main_task_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False))
            f.close()

    def get_task_jsonfile(self):

        self.sub_tasks_path = []
        for file in os.listdir(self.task_sub_dir):
            print('这是file: ',file)
            if '.json' in file and '已抓完' not in file:
                self.sub_tasks_path.append(file)
        print('只是 sub_tasks_path', self.sub_tasks_path)

    def check_task_info(self,module_dir, keywords):

        with open(self.main_task_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for task_info in json_data:
            if module_dir == task_info['module_dir'] and keywords == task_info['keywords']:
                if task_info['is_running'] == 1:
                    print('检测到当前任务正在抓取中, 跳过!!')
                elif task_info['have_end'] == 1:
                    print('检测到当前任务已经抓取完成,跳过')
                else:
                    return 'task_can_do'
            else:
                print('选取对象无法对应,跳过!')

    def get_task_infos(self):
        '''
        获取执行任务的基本信息, 执行任务可以存在多个, 且排队做执行. 选择执行任务时, 任务队列需满足 owning_account(所属账号),have_end(未抓取过),is_running(没在执行),spider_at(抓取平台 win/linux), mode(抓取的方向 全库/病例), 符合这几个条件则进入任务队列排队执行
        :return: 返回self.search_infos 所有的待执行的任务搜索队列
        '''
        self.get_task_jsonfile()
        with open(self.main_task_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        repeat_keywords = []
        # 检查任务信息是否重复
        for base_info in json_data:
            if base_info['module_dir'] == self.module_dir:
                keyword = '{}_{}_{}_{}'.format(base_info['module_dir'],base_info['keywords'],base_info['max_year'],base_info['min_year'])
                if keyword not in repeat_keywords:
                    repeat_keywords.append(keyword)
                else:
                    print('检查到重复任务: {}, 请查看任务列表数据!!'.format(keyword))
                    exit()
            else:
                print('任务总表中没有发现任何有关 {} 的任务信息'.format(self.module_dir))
                exit()

        # # 筛选任务信息
        temp_task_list = [base_info for base_info in json_data if base_info['module_dir'] == self.module_dir and base_info['platform'] == self.platform and base_info['have_end'] != 1 and base_info['is_running'] != 1 and base_info['have_locked']=='no']

        # 筛选子任务信息
        if temp_task_list:
            for main_task_info in temp_task_list:
                task_infos = {}
                print('当前任务长度为: {}'.format(len(task_infos)))

                if len(task_infos) <= self.max_task_mum - 1:
                    task_file_name = '{}_{}.json'.format(main_task_info['module_dir'],main_task_info['keywords'])
                    task_status = self.check_task_info(main_task_info['module_dir'],main_task_info['keywords'])
                    if task_status == 'task_can_do':
                        if task_file_name in self.sub_tasks_path:
                            print('主任务名与子任务文件名称匹配成功: {}'.format(task_file_name))
                            file_path = self.task_sub_dir + '/' + task_file_name
                            with open(file_path,'r',encoding='utf-8') as f:
                                task_info = json.loads(f.read())
                                f.close()
                            # 当前主任务信息
                            self.main_task_info = main_task_info
                            key = main_task_info['module_dir'] + '_' + main_task_info['keywords']
                            # 当前子任务信息
                            # 主任务与子任务一一对应的关系
                            task_infos[key] = task_info
                            yield task_infos
                            # print('这是里面的 task_infos', task_infos)
                        else:
                            print('主任务名与子任务文件名称匹配不上, 或者当前子任务文件不存在 : {}'.format(task_file_name))
                    else:
                        print('检测到任务正在运行中/已经抓取完成, 跳过!!')
                else:
                    print('每个程序获取的最大任务数量不能超过 {} 个'.format(self.max_task_mum))
                    break

            # print('这是获取到的所有任务数据: ',task_infos.keys())
        else:
            print('所有符合条件的任务都已经抓取完成!!')
            exit()

        # exit()
        # if new_list:
        #     self.search_infos = sorted(new_list, key=lambda x: x['level'], reverse=False)
        #     print('这是待抓取任务的优先级排序... ', self.search_infos)
        # else:
        #     print('任务都已经都在运行中/已完成了, 请注意查看并添加新的任务!!!')
        #     exit()

    def login_again(self):

        if hasattr(self,'session') and self.session:
            print('存在 session, 开始清理session中的cookie, 并重新登录!!')
            self.session.cookies.clear()
            self.session = self.zwlogin.login()
        else:
            print('不存在 session, 重新登录!!')
            self.session = self.zwlogin.login()

    def request_list(self,subject_info,title_info):

        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + \
                         self.main_task_info['platform'] + '","Name":"' + self.model_match_data + '","Value":"' + \
                         self.main_task_info[
                             'keywords'] + '","Operate":"%=","BlurType":""}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"1","Title":"","Logic":1,"Items":[{"Key":"' + \
                         title_info['title_text'] + '","Title":"' + title_info['title_text'] + '","Logic":2,"Name":"' + \
                         title_info['title_type'] + '","Operate":"","Value":"' + title_info[
                             'title_text'] + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"' + \
                         subject_info['value'] + '?","Title":"' + subject_info[
                             'subject_name'] + '","Logic":2,"Name":"' + subject_info[
                             'field'] + '","Operate":"","Value":"' + subject_info[
                             'value'] + '?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + self.cur_year + '","Title":"' + self.cur_year + '","Logic":2,"Name":"年","Operate":"","Value":"' + self.cur_year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]},"CodeLang":"ch"}'
        params = {
            'IsSearch': 'true',
            'QueryJson': self.queryjson,
            'SearchSql': self.searchsql,
            'PageName': 'defaultresult',
            'HandlerId': self.HandlerId,
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
            'CurPage': 1,
            'RecordsCntPerPage': self.main_task_info['page_size'],
            'CurDisplayMode': 'listmode',
            'CurrSortField': 'PT',
            'CurrSortFieldType': 'desc',
            'IsSortSearch': 'false',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }
        print('开始发起列表页请求, 目的是获取模块页码数据!!')
        for i in range(self.retry_down_list_max):
            # try:
            time.sleep(random.uniform(3, 5))
            try:
                res = self.session.post(self.list_url, data=params, headers=self.headers_list, timeout=(20, 30))
                print('get_page_num数据请求正常')
            except Exception as e:
                print('请求获取get_page_num时出现错误: {}!!重新获取'.format(repr(e)))
                time.sleep(random.uniform(2, 5))
                if i >= 2:
                    print('获取 最大页码时 连续超过2次出错, 重新登录获取数据!!!')
                    self.get_searchsql()
                continue
            res.encoding = 'utf-8'
            if res.status_code == 200 and '共找到' in res.text:

                html = etree.HTML(res.text)
                try:
                    total_data = html.xpath('//div[@id="countPageDiv"]')[0]
                    total = total_data.xpath('./span[@class="pagerTitleCell"]/em/text()')
                    # total_page = total_data.xpath('./span[@class="countPageMark"]/text()')
                    self.HandlerId = html.xpath('//input[@id="HandlerIdHid"]/@value')[0]
                    print('这是变化后的 handlerid: ', self.HandlerId)
                    if total:
                        total_num = int(total[0].replace(',','').replace('\r\n',''))
                        total_page_num = total_num // self.main_task_info['page_size'] + 1
                        print('当前模块含有 {} 条数据, 共 {} 页'.format(total_num, total_page_num))
                        return total_num,total_page_num
                    else:
                        print('没有获取到模块数据 总数,重新获取')
                        continue
                except Exception as e:
                    print('get_page_num 获取数据时出现问题, 详情为: {}'.format(repr(e)))
                    continue
            elif '抱歉，暂无数据' in res.text:
                print('当前模块没有数据,进入下一模块')
                return 'no_data'
            else:
                if i >= 5:
                    print("超过5次获取列表页总页码失败, 暂停一会儿, 重新获取, 重新登录获取!!".format(i))
                    self.get_searchsql()
                    time.sleep(random.uniform(600, 900))
                elif i >= 2 and i < 5:
                    print("超过2次获取列表页总页码失败, 暂停30~40min重新获取, 重新登录获取!!".format(i))
                    self.get_searchsql()
                    time.sleep(random.uniform(300, 600))
                else:
                    print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                    time.sleep(random.uniform(60, 120))

    def get_page_num(self,subject_info,title_info):
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
            total_data = self.request_list(subject_info, title_info)
            if total_data == 'no_data':
                return 'no_data'
            total_num, total_page_num = total_data

            print('当前模块数据未抓取过, 从最大页码开始抓取, 最大页为网站总页码: {}, 结束页码为: 0'.format(total_page_num))
            min_page = 0
            max_page = total_page_num
            if total_num == 0:
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
                total_data = self.request_list(subject_info, title_info)
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
                        print('网站数据目前还未更新, 或者更新数据不足 {} 条, 不抓取数据!!'.format(self.main_task_info['page_size']))
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
                    total_data = self.request_list(subject_info, title_info)
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

        sql_page = self.mongo_zw_all.find_zw_page_num(self.item['origin_module'])
        print('mongo中获取到的最大 cur_page 为: {}'.format(sql_page))
        return sql_page

    def get_searchsql(self):

        url = 'https://kns.cnki.net/kns8/defaultresult/index'

        for i in range(8):
            try:
                print('进入 get_searchsql')
                self.login_again()
                self.session.get(url, headers=self.headers_init, timeout=(15, 20))
                time.sleep(random.uniform(0, 0.5))
                print('请求url完成!!')
                # cookie_dblang = {
                #     "dblang": "ch"
                # }
                # self.session.cookies.update(cookie_dblang)
                # 获取大的搜索模块基本数据
                header_field = {
                    'Referer': 'https://www.cnki.net/',
                    'User-Agent': random.choice(useragent_pool)
                }
                field_json_url = 'https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6'
                res = self.session.get(field_json_url, headers=header_field,timeout=(20,30))
                print('请求field_json_url完成')
                self.model_match_data = \
                re.findall(r'Text:"' + self.main_task_info['platform'] + '",Value:"(\w+).*?"}', res.text)[0]
                self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + \
                                 self.main_task_info['platform'] + '","Name":"' + self.model_match_data + '","Value":"' + self.main_task_info[
                                     'keywords'] + '","Operate":"%"}],"ChildItems":[]}]}}'
                # 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

                # 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数
                status = self.request_searchsql()
                print('获取status 完成!!')
                if status == "searchsql_ok":
                    print('成功获取到 searchsql 为: {}'.format(self.searchsql))
                elif status == "temp_code_ok":
                    print('临时验证码验证成功,等待10到20分钟,重新执行 get_searchsql')
                    time.sleep(random.uniform(300, 900))
                else:
                    print('reqeust_searchsql 返回结果为: {}'.format(status))
                print('退出 get_searchsql!')
                break

            except:
                print('第 {} 次获取 searchsql 时出现问题, 稍定一下, 重新发起请求!!!'.format(i))
                time.sleep(random.uniform(10,20))
                if i >= 1 and i <= 3:
                    print('第2次请求列表首页出现问题, 稍等一下, 登录后, 重新发起请求!!!')
                    time.sleep(random.uniform(180,300))
                elif i > 3:
                    print('请求列表首页超过3次出现问题, 等待半小时后重新发起请求!!!')
                    time.sleep(random.uniform(600,1200))
                self.login_again()

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

    def request_searchsql(self):

        data = {
            'IsSearch': 'true',
            'QueryJson': self.queryjson,
            'PageName': 'defaultresult',
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
            'CurPage': 1,
            'RecordsCntPerPage': self.main_task_info['page_size'],
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
                        return 'searchsql_ok'
                    else:
                        print('未获取到sqlval, 暂停5秒, 重新请求!!')
                        time.sleep(random.uniform(30,60))

                elif res.status_code == 200 and '请输入验证码' in res.text:
                    print('出现了验证码, 开始识别!')
                    # self.log.warning('出现了验证码, 开始识别!')
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


    def get_page_list(self, subject_info, title_info):

        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + \
                         self.main_task_info['platform'] + '","Name":"' + self.model_match_data + '","Value":"' + \
                         self.main_task_info[
                             'keywords'] + '","Operate":"%=","BlurType":""}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"1","Title":"","Logic":1,"Items":[{"Key":"' + \
                         title_info['title_text'] + '","Title":"' + title_info['title_text'] + '","Logic":2,"Name":"' + \
                         title_info['title_type'] + '","Operate":"","Value":"' + title_info[
                             'title_text'] + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"' + \
                         subject_info['value'] + '?","Title":"' + subject_info[
                             'subject_name'] + '","Logic":2,"Name":"' + subject_info[
                             'field'] + '","Operate":"","Value":"' + subject_info[
                             'value'] + '?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + self.cur_year + '","Title":"' + self.cur_year + '","Logic":2,"Name":"年","Operate":"","Value":"' + self.cur_year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]},"CodeLang":"ch"}'
        params = {
            'IsSearch': 'false',
            'QueryJson': self.queryjson,
            'SearchSql': self.searchsql,
            'PageName': 'defaultresult',
            'HandlerId': self.HandlerId,
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN',
            'CurPage': self.cur_page,
            'RecordsCntPerPage': self.main_task_info['page_size'],
            'CurDisplayMode': 'listmode',
            'CurrSortField': 'PT',
            'CurrSortFieldType': 'desc',
            'IsSortSearch': 'false',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }

        # if self.cur_page > 1:
        #     params['IsSearch'] = 'false'

        print('*' * 20)
        print('这是要看的params: {}'.format(str(params)))
        print('*' * 20)
        for i in range(self.retry_down_list_max):
            self.headers_list['User-Agent'] = random.choice(useragent_pool)
            # 第二次获取根据日期排序的列表数据, 以下可改变页码来获取数据
            try:
                res = self.session.post(self.list_url, data=params, headers=self.headers_list, timeout=(10, 20))
                time.sleep(random.uniform(0,0.3))
            except:
                print('列表页第 {} 次请求超时或读取失败, 休息一下, 重新登录并获取列表页数据!!'.format(i))
                time.sleep(random.uniform(20,30))
                self.get_searchsql()
                continue
            if res.status_code == 200 and ('题名' in res.text and '发表时间' in res.text):
                html = etree.HTML(res.text)
                try:
                    self.HandlerId = html.xpath('//input[@id="HandlerIdHid"]/@value')[0]
                    print('这是变化后的 handlerid: ',self.HandlerId)
                    trs = html.xpath('//table[@class="result-table-list"][1]//tr')[1:]
                except Exception as e:
                    print('摘取错误!!跳过!! 详情: {}'.format(e))
                    continue
                for tr in trs:
                    self.item.clear()
                    print('*' * 20)
                    try:
                        a = tr.xpath('./td[@class="name"]/a')[0]
                        self.item['title'] = a.xpath('string(.)').strip()
                    except:
                        self.item['title'] = ''
                    self.item['origin_module'] = '{}_{}_{}_{}_{}_{}'.format(self.main_task_info['module_dir'],
                                                                            self.main_task_info['keywords'],
                                                                            self.cur_year,
                                                                            subject_info['subject_name'],
                                                                            title_info['title_type'],
                                                                            title_info['title_text'])
                    self.item['date'] = tr.xpath('./td[@class="date"]/text()')[0].strip()
                    name = '{}_{}.pdf'.format(self.item['title'].replace('/', '_'), self.item['date'].replace(' ', '&'))
                    # print('name等于: ', name)
                    file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", name)
                    self.item['file_name'] = file_name
                    duplicate_status = self.redis_zw.set_item('zw_cnki', file_name)
                    time.sleep(random.uniform(0.1, 0.3))
                    if duplicate_status == 1:
                        self.have_spider_num = 0
                        print('是否请求状态为: {}, 之前未请求过, 即将发起请求'.format(duplicate_status))
                        if tr.xpath('./td[@class="name"]/a/@href'):
                            base_source_link = 'https://kns.cnki.net'

                            try:
                                self.item['detail_url'] = urljoin(base_source_link, tr.xpath('./td[@class="name"]/a/@href')[0].strip())
                            except:
                                self.item['detail_url'] = ''
                            try:
                                self.item['author'] = tr.xpath('./td[@class="author"]')[0].xpath('string(.)').strip()
                            except:
                                self.item['author'] = ''
                            try:
                                self.item['source_name'] = tr.xpath('./td[@class="source"]/a/text()')[0].strip()
                            except:
                                self.item['source_name'] = ''
                            try:
                                self.item['source_link'] = urljoin(base_source_link,tr.xpath('./td[@class="source"]/a/@href')[0].strip())
                            except:
                                self.item['source_link'] = ''

                            self.item['source_type'] = tr.xpath('./td[@class="data"]/text()')[0].strip()
                            self.item['cur_page'] = int(self.cur_page)

                            if tr.xpath('./td[@class="download"]/a/text()'):
                                self.item['down_num'] = tr.xpath('./td[@class="download"]/a/text()')[0].strip()
                            else:
                                self.item['down_num'] = 0
                            self.get_pdf_url()
                            if 'pdf_url' in self.item and self.item['pdf_url']:
                                self.down_identify_pdf()
                                time.sleep(random.uniform(0, 1))
                                print('这是获取到的item: ',self.item)
                                self.save()
                            else:
                                print('当前项目没有发现含有pdf_url, 不做下载保存处理!!')
                        else:
                            print('详情页链接地址为空!!')
                        print('*' * 20)
                    else:
                        # print('当前详情页以及pdf文件都已经下载过, 不再继续做处理!!!')
                        # self.havedown_times += 1
                        # if self.havedown_times <= self.have_spider_num_max:
                        #
                        #     # self.log.info('列表页中发现第 {} 次之前连续被下载过的痕迹'.format(self.havedown_times))
                        #     time.sleep(random.uniform(0.1, 0.5))
                        # else:
                        #     print('发现连续之前被下载过的详情及pdf痕迹超过 {} 条,不再下载, 跳过本模块'.format(self.havedown_times))
                        #     self.havedown_times = 0
                        #     return 0
                        self.have_spider_num += 1
                        print('列表页中发现第 {} 次之前连续被下载过的痕迹'.format(self.have_spider_num))
                        if self.have_spider_num >= self.have_spider_num_max:
                            print('连续抓取过数据超过 {} 个, 向后跳 {} 页, 继续抓取!'.format(self.have_spider_num_max,
                                                                           self.turn_page_num))
                            self.cur_page -= self.turn_page_num
                            self.have_spider_num = 0
                            return 'turn_over'

                break
            else:
                print('第 {} 次没有获取到当前列表页的数据,稍等5~10分钟, 接下来重新登录重新获取当前页面的数据'.format(i))
                # self.log.info('没有获取到当前列表页的数据,接下来重新登录重新获取当前页面的数据')
                time.sleep(random.uniform(60, 120))
                self.get_searchsql()

    def get_pdf_url(self):

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
        # if self.pdfdown_fail > 4:
        #     print('连续4次发现pdf文件大小不到50k,稍等一下, 重新登录并获取searchsql!!!')
        #     time.sleep(random.uniform(180,400))
        #     self.get_searchsql()
        #     self.pdfdown_fail = 0

        # 1代表请求成功

        for i in range(5):
            try:
                res = self.session.get(self.item['detail_url'], headers=headers_detail, timeout=(10, 20))
                time.sleep(random.uniform(0.1,0.4))
                if res.status_code == 200 and 'pdfDown' in res.text:

                    print('detail_url 为: ', self.item['detail_url'])
                    print('detail_url_302为: ', res.url)
                    self.item['detail_url'] = res.url
                    detail_html = etree.HTML(res.text)
                    pdf_url = detail_html.xpath('//a[@id="pdfDown"][1]/@href')[0]
                    if 'javascript' not in pdf_url:
                        base_url = 'https://bar.cnki.net'
                        self.item['pdf_url'] = urljoin(base_url, pdf_url)
                        break
                    else:
                        print('详情链接中含有javascript, 页面显示应该是需要充钱付费的, 等待2秒钟, 重新尝试请求, pdf链接地址为: {}'.format(pdf_url))
                        time.sleep(2)
                elif 'CAJ原文下载' in res.text or '分页下载' in res.text:
                    print('当前为 CAJ原文下载, 跳过!! 连接地址为: {}'.format(res.url))
                    time.sleep(random.uniform(0.2, 0.5))
                    self.item['identify_status'] = '含有分页下载'
                    break
                elif 'pdfDown' not in res.text:
                    print('当前页面不含有pdf下载按钮,详情页链接地址为: {}'.format(self.item['detail_url']))
                    self.item['identify_status'] = '无pdf下载'
                    break
                else:
                    print('详情页链接地址请求有问题, 状态不为200 或者其它特殊情况, 请详细查看,详情页链接地址为: {}'.format(self.item['detail_url']))
                    if i >= 2:
                        print('请求页请求连续超过2次, 重新登录之后再次获取!!')
                        time.sleep(random.uniform(2, 3))
                        self.login_again()
            except:
                print('请求详情页第 {} 次出现问题, 休息一下再次请求!!'.format(i))
                time.sleep(random.uniform(5,10))
                if i >= 2:
                    print('请求页请求连续超过2次, 重新登录之后再次获取!!')
                    time.sleep(random.uniform(2,3))
                    self.login_again()



    def down_identify_pdf(self):

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

        for i in range(self.retry_down_pdf_max):
            print('开始下载pdf文件......')
            try:
                # item['pdf_url'] = 'https://kns.cnki.net/kcms/detail/detail.aspx?dbcode=CJFD&dbname=CJFDZHYX&filename=SZBB201808019&uniplatform=NZKPT&v=-VcQfQ2UntzmsOPlJT8_o7bI5XxaP3WR9xxFFoXzmHpGLpvvY9P9FSDkN_ddbncL'
                print('这是初始pdf_url: ',self.item['pdf_url'])
                res = self.session.get(self.item['pdf_url'], headers=headers_pdf, timeout=(10, 20))
                # time.sleep(random.uniform(0, 0.5))
                time.sleep(random.uniform(1,2))
                if '本篇免费，下载阅读' in res.text:
                    print('发现本篇免费, 下载阅读字眼')
                    print('开始处理本篇免费, 下载阅读页数据')
                    html = etree.HTML(res.text)
                    cardorfee_data = html.xpath('//input[@id="CardOrFee"]/@value')
                    if cardorfee_data:
                        cardorfee = cardorfee_data[0]
                    else:
                        print('pdf下载时出现本篇免费, 但未获取到 cardorfee 参数, 设置为 4 ')
                        cardorfee = 4
                    downfilename_data = html.xpath('//input[@id="downfilename"]/@value')
                    if downfilename_data:
                        downfilename = downfilename_data[0]
                    else:
                        print('pdf下载时出现本篇免费, 但未获取到 downfilename 参数, 重新获取数据!!')
                        continue
                    new_pdf_url = 'https://bar.cnki.net/bar/Download/ConfimDownLoadDazong'
                    new_pdf_headers = {
                        # "Host": "bar.cnki.net",
                        "Connection": "keep-alive",
                        "Content-Length": "38",
                        "Cache-Control": "max-age=0",
                        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
                        "sec-ch-ua-mobile": "?0",
                        "sec-ch-ua-platform": "\"Windows\"",
                        "Upgrade-Insecure-Requests": "1",
                        "Origin": "https://bar.cnki.net",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-User": "?1",
                        "Sec-Fetch-Dest": "document",
                        "Referer": self.item['pdf_url'],
                        "Accept-Encoding": "gzip, deflate, br",
                        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
                    }
                    data = {"CardOrFee":cardorfee,"downfilename":downfilename}
                    res = self.session.post(new_pdf_url,data=data,headers=new_pdf_headers,timeout = (20,30))
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
                        print("添加医生信息后的数据为: ", self.item)
                        break

                    elif ('本篇支付' in res.text) or ('没有订购此产品' in res.text) or ('没有此产品的使用权限' in res.text):
                        self.pay_permission += 1
                        print('检测到连续含有本篇支付或者无权限pdf文件第 {} 次,标题为: {}'.format(self.pay_permission, self.item['title']))
                        time.sleep(random.uniform(1, 3))
                        # if i < 2:
                        #     print('当前第 {} 下载需支付pdf文件'.format(i))
                        #     time.sleep(random.uniform(0.5,1))
                        #     continue
                        if self.pay_permission > 8:
                            print('检测到连续含有本篇支付或者无权限pdf文件超过6次, 暂停1min, 重新登录获取文件数据!!')
                            time.sleep(60)
                            self.login_again()
                            self.pay_permission = 0
                        # print('检测到含有本篇支付或者无使用权限存在, 标题为: ', item['title'])
                        self.item['need_pay'] = '需支付/无访问权限'
                        self.item['doctor_info'] = ''
                        self.item['phones'] = ''
                        self.item['identify_status'] = '未识别'
                        break

                    elif int(res.headers['Content-Length']) < min_limit:

                        self.pay_permission = 0
                        print('注意!!当前的pdf文件下载第 {} 次小于 50 k, 重新下载, 当前pdfdown_fail的值为: {}'.format(i,self.pdfdown_fail))
                        time.sleep(random.uniform(5, 10))
                        self.item['doctor_info'] = ''
                        self.item['phones'] = ''
                        self.item['identify_status'] = '文件过小未下载'
                        self.pdfdown_fail += 1

                        # if i >= 2:
                        #     print('超过3次下载pdf文件失败,不再下载!')
                        #     break
                        # if i >= 1:
                        #     print('下载小于50k超过2次, 重新登录并下载')
                        #     self.login_again()
                        if self.pdfdown_fail >= 11:
                            print('检测到连续下载pdf文件失败超过 11 次, 暂停1min, 重新登录获取文件数据!!')
                            time.sleep(60)
                            self.login_again()
                            self.pdfdown_fail = 0
                        break

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
        if 'phones' in self.item and self.item['phones']:
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
            print('发现新数据, 但没有手机号, 将手机号重置为空, 放入zw_all中')
            self.item['phones'] = ''
            self.mongo_zw_all.insert(self.item)
        self.item.clear()



    def run(self):

        # # 获取子任务详情数据
        # with open(self.ori_jsondata_url, 'r', encoding='utf-8') as f:
        #     data = f.read()
        # json_data = json.loads(data)

        for i in range(3):
            try:
                # 排队执行所有待抓取的任务
                # 排队执行所有待抓取的任务
                for task_data in self.get_task_infos():
                    for task_name, task_info in task_data.items():
                        print(task_name)
                        self.update_task(self.main_task_info, have_start=1, is_running=1)
                        self.get_searchsql()
                        for year in range(self.main_task_info['max_year'], self.main_task_info['min_year'], -1):
                            self.cur_year = str(year)
                            module_end_year_data = '{}_{}_{}'.format(self.main_task_info['module_dir'],self.main_task_info['keywords'],self.cur_year)
                            year_spider_status = self.mongo_zw_all.get_module_end_year(module_end_year_data)
                            if year_spider_status != 'cur_year_over':
                                moudle_datas = task_info[self.cur_year]
                                for index, moudle_data in enumerate(moudle_datas):
                                    subject_info = moudle_data['subject_info']
                                    for title_info in moudle_data['title_info'].values():
                                        little_key = title_info['title_type'] + '__' + title_info['title_text']
                                        print('当前是{}_{}, {}年, 学科为: {}, 标题为: {}'.format(self.main_task_info['module_dir'],
                                                                                        self.main_task_info['keywords'], year,
                                                                                        str(subject_info['subject_name']),
                                                                                        little_key))
                                        # time.sleep(2)
                                        self.item['origin_module'] = '{}_{}_{}_{}_{}_{}'.format(self.main_task_info['module_dir'],
                                                                                        self.main_task_info['keywords'],
                                                                                        self.cur_year,subject_info['subject_name'],title_info['title_type'],title_info['title_text'])
                                        data = self.get_page_num(subject_info,title_info)
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
                                                # print('这是要看的item值',self.item)
                                                if 'origin_module' not in self.item:
                                                    self.item['origin_module'] = '{}_{}_{}_{}_{}_{}'.format(
                                                        self.main_task_info['module_dir'],
                                                        self.main_task_info['keywords'],
                                                        self.cur_year, subject_info['subject_name'], title_info['title_type'],
                                                        title_info['title_text'])
                                                print('当前是{} 第 {} 页数据'.format(self.item['origin_module'],self.cur_page))
                                                spider_status = self.get_page_list(subject_info,title_info)
                                                if spider_status == 'turn_over':
                                                    print('检测到当前发生了页面跳过, 跳转之后的页码为: {}'.format(self.cur_page))
                                                    time.sleep(random.uniform(2, 5))
                                                self.cur_page -= 1
                                        else:
                                            print('开始抓取下一个模块数据!')
                                self.mongo_zw_all.insert_module_end_year(module_end_year_data)
                            else:
                                print('当前年已经抓去过, 不再继续抓取!!')

                    self.update_task(self.main_task_info, have_end=1, is_running=0, cur_year=self.cur_year)
                break
            except Exception as e:
                print('抓取时出现问题, 休息10~15分钟, 详情为: {}'.format(repr(e)))
                print(f'error file:{e.__traceback__.tb_frame.f_globals["__file__"]}')
                print(f"error line:{e.__traceback__.tb_lineno}")
                time.sleep(random.uniform(600, 900))
                self.update_task(self.main_task_info, is_running=0, cur_year=self.cur_year)
                time.sleep(random.uniform(5,10))


# # 新增时的思路是: 获取数据库最大的日期与对应的title,锁定到具体在第几页, 然后倒着去获取数据
# # queryjson里面的name决定了大块的搜索范围, 如: 参考文献: 临床医学: RF  作者单位: 医院: AF, 可以请求 https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6获取对应的json标记
