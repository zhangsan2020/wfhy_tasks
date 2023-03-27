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
from task.common.useragent import useragent_pool
from task.zhiwang.zw_login import ZwLogin

class ZwModules():

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
        self.list_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
        self.identify = CurIdentify()
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
        # self.mongo_zw_all = ZwMongo('wfhy_update', 'zw_all')
        # self.mongo_zw_commit = ZwMongo('wfhy_commit', 'zw_commit')
        # self.redis_zw = ZwRedis()
        # self.redis_all_phones = ZwRedis()
        # self.log = FrameLog('zw_cnki').get_log()
        self.retry_getsearchsql = 1
        self.HandlerId = 0
        self.page_items_retry = 0
        # 连续第多少次重新下载, 如果检测到列表页面中detail与pdf连续10次之前被下载过, 将不再对当前模块发起请求, 直接接入下一模块
        self.havedown_times = 1
        # self.years = ['2022','2021','2020','2019']
        self.pdfdown_fail = 0
        self.pay_permission = 0
        self.item = {}
        self.retry_down_pdf_max = 5
        self.retry_down_list_max = 10
        self.have_spider_num = 0
        self.have_spider_num_max = 255
        self.turn_page_num = 1
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
        temp_task_list = [base_info for base_info in json_data if base_info['module_ok']=='no']
        return temp_task_list

    def login_again(self):

        if hasattr(self,'session') and self.session:
            print('存在 session, 开始清理session中的cookie, 并重新登录!!')
            self.session.cookies.clear()
            self.session = self.zwlogin.login()
        else:
            print('不存在 session, 重新登录!!')
            self.session = self.zwlogin.login()

    def get_searchsql(self):

        url = 'https://kns.cnki.net/kns8/defaultresult/index'

        for i in range(8):
            try:
                self.login_again()
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
                self.model_match_data = \
                re.findall(r'Text:"' + self.main_task_info['platform'] + '",Value:"(\w+).*?"}', res.text)[0]
                self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + \
                                 self.main_task_info['platform'] + '","Name":"' + self.model_match_data + '","Value":"' + self.main_task_info[
                                     'keywords'] + '","Operate":"%"}],"ChildItems":[]}]}}'
                # 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

                # 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数
                status = self.request_searchsql()

                if status == "searchsql_ok":
                    print('成功获取到 searchsql 为: {}'.format(self.searchsql))
                elif status == "temp_code_ok":
                    print('临时验证码验证成功,等待10到20分钟,重新执行 get_searchsql')
                    time.sleep(random.uniform(300, 900))
                else:
                    print('reqeust_searchsql 返回结果为: {}'.format(status))
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

    def request_second_module(self):

        modlue_url = 'https://kns.cnki.net/kns8/Group/Result'
        # self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"篇名","Name":"TI","Value":"临床","Operate":"%=","BlurType":""}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"2022","Title":"2022","Logic":2,"Name":"年","Operate":"","Value":"2022","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]},"CodeLang":"ch"}'
        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + self.main_task_info['platform'] + '","Name":"TI","Value":"' + self.main_task_info['keywords'] + '","Operate":"%=","BlurType":""}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + self.cur_year + '","Title":"' + self.cur_year + '","Logic":2,"Name":"年","Operate":"","Value":"' + self.cur_year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]},"CodeLang":"ch"}'
        print(self.queryjson)
        headers = {
                "Host": "kns.cnki.net",
                "Connection": "keep-alive",
                "Content-Length": "1040",
                "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "sec-ch-ua-platform": "\"Windows\"",
                "Origin": "https://kns.cnki.net",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://kns.cnki.net/kns8/defaultresult/index",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
        params = {
            'QueryJson': self.queryjson,
        }
        res = self.session.post(modlue_url,data=params,headers = headers)

        if res.status_code == 200:
            html = etree.HTML(res.text)
            field = html.xpath('//dd[@tit="学科"][1]/@field')[0].strip()
            second_module_list = html.xpath('//dd[@tit="学科"]//li')
            first_module = []
            for second_module in second_module_list:
                self.second_module_info = {}
                self.second_module_info['subject_name'] = second_module.xpath('./input/@text')[0].strip()
                self.second_module_info['value'] = second_module.xpath('./input/@value')[0].strip()
                self.second_module_info['field'] = field
                print('二级数据为: ',self.second_module_info)
                # self.get_searchsql()
                self.cur_modules = {}
                self.request_third_module()

    def request_third_module(self):

        modlue_url = 'https://kns.cnki.net/kns8/Group/Result'
        # self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"篇名","Name":"TI","Value":"临床","Operate":"%=","BlurType":""}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"E056?","Title":"中医学","Logic":2,"Name":"专题子栏目代码","Operate":"","Value":"E056?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"2022","Title":"2022","Logic":2,"Name":"年","Operate":"","Value":"2022","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]},"CodeLang":"ch"}'
        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + self.main_task_info['platform'] + '","Name":"TI","Value":"' + self.main_task_info['keywords'] + '","Operate":"%=","BlurType":""}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"' + self.second_module_info['value'] + '?","Title":"' + self.second_module_info['subject_name'] + '","Logic":2,"Name":"' + self.second_module_info['field'] + '","Operate":"","Value":"' + self.second_module_info['value'] + '?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + self.cur_year + '","Title":"' + self.cur_year + '","Logic":2,"Name":"年","Operate":"","Value":"' + self.cur_year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]},"CodeLang":"ch"}'
        headers = {
                "Host": "kns.cnki.net",
                "Connection": "keep-alive",
                "Content-Length": "1502",
                "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "sec-ch-ua-platform": "\"Windows\"",
                "Origin": "https://kns.cnki.net",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://kns.cnki.net/kns8/defaultresult/index",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }
        params = {
            'QueryJson': self.queryjson,
        }
        res = self.session.post(modlue_url,data=params,headers = headers)

        if res.status_code == 200:
            self.third_module_info = {'title_info':{}}
            html = etree.HTML(res.text)
            # 获取主要主题
            zhuyao_title_type = html.xpath('//dd[@tit="主要主题"][1]/@field')[0].strip()
            zhuyao_module_list = html.xpath('//dd[@tit="主要主题"][1]//li')
            for zhuyao_module in zhuyao_module_list:
                zhuyao_title_text = zhuyao_module.xpath('./input/@text')[0].strip()
                key = '{}__{}'.format(zhuyao_title_type,zhuyao_title_text)
                self.third_module_info['title_info'][key]={'title_type':zhuyao_title_type,'title_text':zhuyao_title_text}
            # 获取次要主题
            ciyao_title_type = html.xpath('//dd[@tit="次要主题"][1]/@field')[0].strip()
            ciyao_module_list = html.xpath('//dd[@tit="次要主题"][1]//li')
            for ciyao_module in ciyao_module_list:
                ciyao_title_text = ciyao_module.xpath('./input/@text')[0].strip()
                key = '{}__{}'.format(ciyao_title_type,ciyao_title_text)
                self.third_module_info['title_info'][key]={'title_type':ciyao_title_type,'title_text':ciyao_title_text}
            print('三级数据为: ',self.third_module_info)
            self.cur_modules['subject_info'] = self.second_module_info
            self.cur_modules.update(self.third_module_info)
            print(self.cur_modules)
            self.all_modules[self.cur_year].append(self.cur_modules)
            print(self.all_modules)
    def get_modules(self):
        self.get_searchsql()
        self.request_second_module()

    def run(self):
        '''
        适用于抓取单一平台模块, 如只抓取篇名, 多平台代码参数不一致, 后续可做升级
        :return:
        '''
        # # 获取子任务详情数据

        for i in range(3):
            try:
                    # 排队执行所有待抓取的任务
                task_infos = self.get_task_infos()
                print(task_infos)
                if task_infos:
                    for main_task_info in task_infos:
                        self.all_modules = {}
                        print(main_task_info)
                        self.main_task_info = main_task_info
                        json_path = '{}/{}_{}.json'.format(self.task_sub_dir,self.main_task_info['module_dir'],self.main_task_info['keywords'])
                        print(json_path)
                        if os.path.exists(json_path):
                            print('当前子任务文件已存在')

                            with open(json_path,'r',encoding='utf-8') as f:
                                data = f.read()
                            if data:
                                print('当前子任务文件已存在,且存在数据, 程序将以此作为基础进行模块数据抓取!!')
                                self.all_modules = json.loads(data)
                            else:
                                print('当前子任务文件已存在,但不存在数据')
                        else:
                            print('不存在子任务文件,即将从 零 开始获取子模块数据!!')

                        self.update_task(self.main_task_info, module_ok='no')
                        for year in range(self.main_task_info['max_year'],self.main_task_info['min_year'],-1):
                            self.cur_year = str(year)
                            if self.cur_year not in self.all_modules:
                                print('开始抓取模块: {}_{}_{}年的模块数据'.format(self.main_task_info['module_dir'],self.main_task_info['keywords'],self.cur_year))
                                time.sleep(random.uniform(5,10))
                                self.all_modules[self.cur_year] = []
                                self.get_modules()
                            else:
                                print('all_modules中已存在 {} 年数据, 不再重复抓取, 开始获取下一年模块数据'.format(self.cur_year))
                                time.sleep(5)
                                continue
                        with open(json_path,'w',encoding='utf-8') as f:
                            f.write(json.dumps(self.all_modules,ensure_ascii=False))
                            f.close()
                        self.update_task(self.main_task_info, module_ok='yes')
                    break
                else:
                    print('所有待抓取任务的子模块数据都已经获取完成!!')
                    break
            except Exception as e:
                print('抓取时出现问题, 休息10~15分钟, 详情为: {}'.format(repr(e)))
                print(f'error file:{e.__traceback__.tb_frame.f_globals["__file__"]}')
                print(f"error line:{e.__traceback__.tb_lineno}")
                time.sleep(random.uniform(600, 900))
                self.update_task(self.main_task_info,module_ok='yes')
                time.sleep(random.uniform(5,10))


# # 新增时的思路是: 获取数据库最大的日期与对应的title,锁定到具体在第几页, 然后倒着去获取数据
# # queryjson里面的name决定了大块的搜索范围, 如: 参考文献: 临床医学: RF  作者单位: 医院: AF, 可以请求 https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6获取对应的json标记
