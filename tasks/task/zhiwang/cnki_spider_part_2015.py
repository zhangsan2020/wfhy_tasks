import hashlib
import json
import os
import random
import re
from datetime import datetime
from urllib.parse import urljoin

# from jsonpath import jsonpath
from lxml import etree
import ddddocr
import requests
import time
from requests.adapters import HTTPAdapter
from .zw_common import user_info, headers_list, choice_moudle
from .cur_identify import CurIdentify
from ..SqlSave.mongo_store import MongoStore
from .redis_zw import ZwRedis
from ..common.log import FrameLog
from ..common.useragent import useragent_pool



class ZwSpider():

    def __init__(self):

        self.headers_init = {
            'User-Agent': random.choice(useragent_pool)
        }
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.list_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
        self.userinfo = user_info
        self.headers_list = headers_list
        # self.searchinfo = {'title': '作者单位', 'keywords': '医院'}
        self.searchinfo = {'model': '作者单位', 'keywords': '医院'}
        self.dir_pdfs = 'E:/zhihu_pdfs/'  # 末尾一定要加上 / , 否则将会自动使用\做填充, 路径会出现问题
        self.identify = CurIdentify()
        self.mongo_zw_all = MongoStore('wfhy_update','zw_all')
        self.mongo_zw_commit = MongoStore('wfhy_commit','zw_commit')
        self.redis_zw = ZwRedis()
        self.log = FrameLog('zw_cnki').get_log()
        self.retry_getsearchsql = 1
        self.HandlerId = 0
        self.page_items_retry = 0
        # 连续第多少次重新下载, 如果检测到列表页面中detail与pdf连续10次之前被下载过, 将不再对当前模块发起请求, 直接接入下一模块
        self.havedown_times = 1
        # self.years = ['2022','2021','2020','2019']
        self.pdfdown_fail = 0

    def get_userinfo(self):

        userinfo = random.choice(self.userinfo)
        return userinfo

    def login(self):

        user_agent = random.choice(useragent_pool)
        self.headers_init['User-Agent'] = user_agent
        self.headers_list['User-Agent'] = user_agent
        self.log.info('开始登录,请稍等...')
        time.sleep(1)
        userinfo = self.get_userinfo()
        print('当前用户信息为: ', userinfo)
        self.log.info('当前用户信息为: {}'.format(userinfo))
        username = userinfo['username']
        password = userinfo['password']
        img_retry = 1
        imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
        self.log.info('请求并识别验证码!!')
        res = self.session.get(imgcode_url, headers=self.headers_init,timeout=(5,20))
        with open('imgcode.jpg', 'wb') as f:
            f.write(res.content)
        code_str = self.get_checkcode('imgcode.jpg')
        print('验证码字符串为: ', code_str)
        self.log.info('验证码识别结果为: {}'.format(code_str))
        time_ = int(time.time() * 1000)
        url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&checkCode={}&p=0&_={}'.format(
            username, password, code_str, time_)
        res = self.session.get(url, headers=self.headers_init, timeout=(5,20))
        if '验证码不正确' in res.text:
            if img_retry <= 8:
                print('验证码识别出错, 正在重新识别, 请稍后!!!')
                self.log.info('验证码识别出错, 正在发起请求进行识别重新识别, 请稍后!!!')
                self.login()
                time.sleep(2)
        elif '登录失败，没有该用户' in res.text:
            print('请确认账号密码!')
            self.log.info('登录失败,请确认账号密码,我将发起重新登录!!')
            self.login()
        elif '登录成功' not in res.text:
            print(res.text)
            self.log.info('恭喜你登录成功!!')
        else:
            print('登录成功!!')

    def get_checkcode(self, img):

        ocr = ddddocr.DdddOcr(old=True)
        # 第一个验证截图保存：verification_code_1.png
        with open(img, 'rb') as f:
            image = f.read()
        res = ocr.classification(image)
        return res

    def search_first_match(self,all_data, search_data):
        jsondatas = json.loads(all_data)
        # key_datas = {}
        key_datas = []
        for jsondata in jsondatas:
            flag_data = jsonpath(jsondata, '$.Value[*].FieldList[?(@.Text=="{}")]'.format(search_data))
            if flag_data:
                search_table = jsonpath(jsondata, '$.key')[0]
                search_key = jsonpath(flag_data, '$[*].Text')[0]
                search_value = re.findall('\w+', jsonpath(flag_data, '$[*].Value')[0])[0]
                # key_datas[search_table] = {search_key: search_value}
                key_datas.append(search_key)
                key_datas.append(search_value)
                key_data = set(key_datas)
                if len(key_data) == 2:
                    return key_data
                else:
                    print('一级搜索的搜索模式不对,表对应标识出现了3种, 请检查, 程序退出!!')
                    exit()

    def get_choice_item(self):
        '''
        获取左侧筛选项
        :return:
        '''

        #         data3 = {
        #             'queryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"2022","Title":"2022","Logic":2,"Name":"年","Operate":"","Value":"2022","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]}}'
        #         }
        #
        #         headers = {
        #             'Accept-Language': 'zh-CN,zh;q=0.9',
        #             'Connection': 'keep-alive',
        #             # 'Content-Length': 986,
        #             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #             'Host': 'kns.cnki.net',
        #             'Origin': 'https://kns.cnki.net',
        #             'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
        #             'Sec-Fetch-Mode': 'cors',
        #             'Sec-Fetch-Site': 'same-origin',
        #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        #             'X-Requested-With': 'XMLHttpRequest'
        #         }
        #         result_url = 'https://kns.cnki.net/kns8/Group/Result'
        #         res = self.session.post(result_url,data=data3,headers=headers)

        # headers_ = {
        #     'Origin': 'https://kns.cnki.net',
        #     'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
        #     'Sec-Fetch-Mode': 'cors',
        #     'Sec-Fetch-Site': 'same-site',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
        # }
        # url_w = 'https://recom.cnki.net/api/recommendations/words/union?w=%E5%8C%BB%E9%99%A2&top=14'
        # res = self.session.get(url_w,headers=headers_)
        # print(res.text)
        # self.init_GetGridTableHtml()
        data = {
            'queryJson': self.queryjson,
        }
        # print('result链接data数据: ', data)
        headers = {
            'Connection': 'keep-alive',
            # 'Content-Length': '498',
            'Host': 'kns.cnki.net',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://kns.cnki.net',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        choice_url = 'https://kns.cnki.net/kns8/Group/Result'
        res = self.session.post(choice_url, data=data, headers=headers)
        # print('这是要看的文本数据', res.text)
        group_datas = {}
        if res.status_code == 200 and '发表年度' in res.text:
            html = etree.HTML(res.text)
            # group_datas['years'] = html.xpath('//dd[@tit="发表年度"]//li/input/@text')
            # 学科
            group_datas['subject'] = html.xpath('//dd[@tit="学科"]//li/input/@text')
            # 主题
            group_datas['topic'] = html.xpath('//dd[@tit="主要主题"]//li/input/@text')
            group_datas['topic'].extend(html.xpath('//dd[@tit="次要主题"]//li/input/@text'))

            # group_datas['study_level'] = html.xpath('//dd[@tit="研究层次"]//li/input/@text')
            # print(group_datas)
            return group_datas
        else:
            print('未获取到左侧筛选数据, 退出!!')

    def get_searchsql(self):

        url = 'https://kns.cnki.net/kns8/defaultresult/index'
        self.session.get(url, headers=self.headers_init, timeout=(5,20))
        self.login()
        cookie_dblang = {
            "dblang": "ch"
        }
        self.session.cookies.update(cookie_dblang)
        headers_1 = {
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        print('进来了')
        headers_0 = {
            'Host': 't.cnki.net',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type,language,uniplatform,unitoken',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        self.session.options('https://t.cnki.net/collect/ux-api/v1/app/batch-trace',headers=headers_0)
        res = self.session.post('https://t.cnki.net/collect/ux-api/v1/app/batch-trace',headers=headers_0)
        print(res.text)
        res = self.session.get('https://kns.cnki.net/kns8/DefaultResult/_LoadSearchFields?dbcode=CFLS',headers=headers_1)
        # print(res.text)
        res = self.session.get('https://recsys.cnki.net//RCDService/api/RecSysOpenApi/HotWordsStat?platformURL=kns.cnki.net%2Fkns8%40KNS8&statPeriod=week',headers=headers_1)
        print(res.text)
        # exit()
        # 获取大的搜索模块基本数据
        header_field = {
            'Referer': 'https://www.cnki.net/',
            'User-Agent': random.choice(useragent_pool)
        }
        field_json_url = 'https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6'
        res = self.session.get(field_json_url,headers=header_field)
        # print(res.text)
        # jsondata = re.findall('var fieldJsonN=(.*)', res.text)[0].replace(';','').replace('Key:','"key":').replace('Value:','"Value":').replace('FieldList:','"FieldList":').replace('ColName:','"ColName":').replace('Text:','"Text":')
        # # print(jsondata)
        # db_model = self.search_first_match(jsondata,self.searchinfo['model'])
        # print(db_model)
        self.searchinfo['model_match_data'] = re.findall(r'Text:"' + self.searchinfo['model'] + '",Value:"(\w+).*?"}', res.text)[0]
        print(self.searchinfo)
        # exit()
        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' + self.searchinfo['model'] + '","Name":"' + self.searchinfo['model_match_data'] + '","Value":"' + self.searchinfo[
                             'keywords'] + '","Operate":"%"}],"ChildItems":[]}]}}'
        data = {
            'IsSearch': 'true',
            'QueryJson': self.queryjson,
            'PageName': 'defaultresult',
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
            'CurPage': 1,
            'RecordsCntPerPage': 20,
            'CurDisplayMode': 'listmode',
            'CurrSortField': '',
            'CurrSortFieldType': 'desc',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }
        # print('*'*20)
        # print('这是要看的data: {}'.format(str(data)))
        # print('*' * 20)
        # 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

        # 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数
        # self.get_resulturl_data()
        self.headers_list['User-Agent'] = random.choice(useragent_pool)
        res = self.session.post(self.list_url, data=data, headers=self.headers_list, timeout=(5,20))

        if res.status_code == 200 and ('题名' in res.text and '发表时间' in res.text):
            html = etree.HTML(res.text)
            searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
            if searchsql_data:
                searchsql = searchsql_data[0]
                self.searchsql = searchsql
                self.retry_getsearchsql = 0
        else:
            if self.retry_getsearchsql <= 3:
                self.retry_getsearchsql += 1
                print('当前是第 {} 次获取searchsql'.format(self.retry_getsearchsql))
                self.log.warning('当前是第 {} 次获取searchsql'.format(self.retry_getsearchsql))
                time.sleep(random.uniform(1,3))
                self.get_searchsql()
            else:
                print('3次获取searchsql未能拿到数据, 退出程序!!')
                self.log.error('3次获取searchsql未能拿到数据, 退出程序!!')
                exit()
        # self.get_resulturl_data()
        url_2 = 'https://kns.cnki.net/kns8/Group/Result'
        data = {
            'queryJson':'{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}"'
        }
        headers_2 = {
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
            'Accept-Encoding': 'gzip, deflate, br',
            'Origin': 'https://kns.cnki.net',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'

        }
        res = self.session.post(url_2,data=data,headers=headers_2)
        print(res.text)
        exit()
    def get_resgroup(self):

        headers = {
            'Host': 'kns.cnki.net',
            'Connection': 'keep-alive',
            'Content-Length': '494',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://kns.cnki.net',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        data = {
            'queryJson':self.queryjson,
            'handleid':	self.HandlerId
        }
        res = self.session.post('https://kns.cnki.net/kns8/Group/ResGroup',data=data,headers=headers)
        print('groupurl数据返回为: ', res.text)

    def get_resulturl_data(self):

        data1 = {
            'queryJson': self.queryjson,
            'groupId': '3'
        }
        data2 = {
            'queryJson': self.queryjson,
            'groupId': '4'
        }
        url = 'https://kns.cnki.net/kns8/Group/SingleResult'
        res = self.session.post(url,data=data1,headers = self.headers_init)
        print('这是模拟',res.text)
        res = self.session.post(url,data=data2,headers = self.headers_init)
        print(res.text)


    def get_page_items(self,page_num,year,sub_info,stu_info):

        self.queryjson = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"'+ self.searchinfo['model'] +'","Name":"' + self.searchinfo['model_match_data'] + '","Value":"' + self.searchinfo['keywords'] + '","Operate":"%"}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"'+ sub_info[1] +'?","Title":"' + sub_info[0] + '","Logic":2,"Name":"' + choice_moudle['subjects']['field'] + '","Operate":"","Value":"' + sub_info[1] + '?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + year + '","Title":"' + year + '","Logic":2,"Name":"年","Operate":"","Value":"' + year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"4","Title":"","Logic":1,"Items":[{"Key":"' + stu_info[1] + '","Title":"' + stu_info[0] + '","Logic":2,"Name":"' + choice_moudle['study_level']['field'] + '","Operate":"","Value":"' + stu_info[1] + '","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]}}'
        params = {
            'IsSearch': 'true',
            'QueryJson': self.queryjson,
            'SearchSql': self.searchsql,
            'PageName': 'defaultresult',
            'HandlerId': self.HandlerId,
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
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
        print('*'*20)
        print('这是要看的params: {}'.format(str(params)))
        print('*' * 20)
        self.headers_list['User-Agent'] = random.choice(useragent_pool)
        # 第二次获取根据日期排序的列表数据, 以下可改变页码来获取数据
        res = self.session.post(self.list_url, data=params, headers=self.headers_list, timeout=(5,20))
        # print(res.text)
        # exit()
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
                        item['title'] = tr.xpath('./td[@class="name"]/a/text()')[0].strip()
                    except:
                        self.page_items_retry += 1
                        if self.page_items_retry < 3:
                            print('没有获取到列表页信息, 可能遇到反爬, 等待一分钟重新登录, 获取该页面, 第 {} 页'.format(page_num))
                            self.log.warning('没有获取到列表页信息, 可能遇到反爬, 等待一分钟重新登录, 获取该页面, 第 {} 页'.format(page_num))
                            time.sleep(60)
                            self.get_searchsql()
                            page_items = self.get_page_items(page_num,year,sub_info,stu_info)
                        else:
                            self.page_items_retry = 0
                            page_items = ''
                            print('当前列表页重复请求3次, 都没有获取到数据, 停止请求, 即将进入到下一模块...')
                            self.log.error('当前列表页重复请求3次, 都没有获取到数据, 停止请求, 即将进入到下一模块...')
                        return page_items
                    item['detail_url'] = urljoin(base_source_link, tr.xpath('./td[@class="name"]/a/@href')[0].strip())
                    item['author'] = tr.xpath('./td[@class="author"]')[0].xpath('string(.)').strip()
                    try:
                        item['source_name'] = tr.xpath('./td[@class="source"]/a/text()')[0].strip()
                    except:
                        item['source_name'] = ''
                    item['source_link'] = urljoin(base_source_link,
                                                  tr.xpath('./td[@class="source"]/a/@href')[0].strip())
                    item['date'] = tr.xpath('./td[@class="date"]/text()')[0].strip()
                    item['source_type'] = tr.xpath('./td[@class="data"]/text()')[0].strip()
                    if tr.xpath('./td[@class="download"]/a/text()'):
                        item['down_num'] = tr.xpath('./td[@class="download"]/a/text()')[0].strip()
                    else:
                        item['down_num'] = 0
                else:
                    print('详情页链接地址为空!!')

                page_items.append(item)
            if page_items:
                return page_items
        else:
            print('没有获取到当前列表页的数据,接下来重新登录重新获取当前页面的数据')
            self.log.info('没有获取到当前列表页的数据,接下来重新登录重新获取当前页面的数据')
            time.sleep(random.uniform(5,10))
            self.get_searchsql()
            time.sleep(random.uniform(5, 10))
            return
            # page_items = self.get_page_items(page_num,year,sub_info,stu_info)
            # return page_items

    def request_duplite(self,item_str):
        m = hashlib.md5()
        m.update(item_str.encode())
        md5_url = m.hexdigest()
        # print(item_str, md5_url)
        return md5_url

    def init_GetGridTableHtml(self):

        url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
        data = {
            'IsSearch': 'true',
            'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]}]}}',
            'PageName': 'defaultresult',
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
            'CurPage': '1',
            'RecordsCntPerPage': '20',
            'CurDisplayMode': 'listmode',
            'CurrSortField':'PT',
            'CurrSortFieldType': 'desc',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }
        res = self.session.post(url,data=data,headers=self.headers_list)
        # print(res.text)



    def after_request_list(self,page_num):

        url = 'https://kns.cnki.net/kns8/Download/ValidRight'
        data = {
            'PageName':'defaultresult',
            'HandlerId':self.HandlerId,
            'SearchSql':self.searchsql,
            'DBCode':'CFLS',
            'CurItem':page_num * 20 + 1,
            'PageSize':20
        }
        res = self.session.post(url,data=data,headers=self.headers_list)
        print('这是after 数据: ',res.text)
        # exit()
    def get_result_year(self):
        data = {"Platform": "", "DBCode": "CFLS", "KuaKuCode": "CJFQ,CDMD,CIPD,CCND,CISD,SNAD,BDZK,CCJD,CCVD,CJFN",
             "QNode": {"QGroup": [{"Key": "Subject", "Title": "", "Logic": 1,
                                   "Items": [{"Title": "作者单位", "Name": "AF", "Value": "医院", "Operate": "%"}],
                                   "ChildItems": []}, {"Key": "SCDBGroup", "Title": "", "Logic": 1, "Items": [],
                                                       "ChildItems": [{"Key": "3", "Title": "", "Logic": 1, "Items": [
                                                           {"Key": "2022", "Title": "2022", "Logic": 2, "Name": "年",
                                                            "Operate": "", "Value": "2022", "ExtendType": 0,
                                                            "ExtendValue": "", "Value2": "", "BlurType": ""}],
                                                                       "ChildItems": []}]}]}}

        url = 'https://kns.cnki.net/kns8/Group/Result'
        res = self.session.post(url,data=data,headers=self.headers_list)
        print(res.text)
    def get_page_list(self):
        # self.get_searchsql()
        # self.get_result_year()
        # exit()
        # years = choice_moudle['years'][]
        # for year in years:
        year = '2015'
        for subject_info in choice_moudle['subjects']['info'].items():
            # sub_field = choice_moudle['subjects']['field']
            for study_info in choice_moudle['study_level']['info'].items():

                # stu_field = choice_moudle['study_level']['field']
                for page_num in range(1, 301):
                    print('***'*20)
                    print('当前是 {} 年, 学科为: {}, 研究层次为: {} 中的第 {} 页数据'.format(year,str(subject_info),str(study_info),page_num))
                    print('***'*20)
                    self.log.info('当前是 {} 年, 学科为: {}, 研究层次为: {} 中的第 {} 页数据'.format(year,str(subject_info),str(study_info),page_num))
                    time.sleep(random.uniform(1, 4))
                    page_items = self.get_page_items(page_num,year,subject_info,study_info)
                    # print('这是要看的items数据: ',page_items)
                    if page_items:
                        status = self.download_detail_pdf(page_items)
                        if status == 0:
                            print('列表页连续超过10条详情及pdf数据之前被下载过, 说明当前模块之后的数据都已被下载过, 不再继续请求')
                            self.log.info('列表页连续超过10条详情及pdf数据之前被下载过, 说明当前模块之后的数据都已被下载过, 不再继续请求')
                            break
                    else:
                        print('当前搜索没有数据了, 开始进行新的搜索模块!!')
                        time.sleep(1)
                        break
                print('开始进入下一模块...., 请稍后!!')
                time.sleep(3)
                # self.get_choice_item()


    def parse_detail_html(self, html):

        detail_html = etree.HTML(html)
        pdf_url_data = detail_html.xpath('//a[@id="pdfDown"]/@href')[0]
        base_url = 'https://bar.cnki.net'
        pdf_url = urljoin(base_url, pdf_url_data)
        return pdf_url

    def download_detail_pdf(self, page_item_data):

        # print('这是要看的数据 page_item_data:  ', page_item_data)
        headers_detail = {

            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': random.choice(useragent_pool),
            'sec-ch-ua-platform': '"Windows"',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'

        }
        if self.pdfdown_fail > 4:
            print('连续4次发现pdf文件大小不到50k,重新登录并获取searchsql!!!')
            self.get_searchsql()
            self.pdfdown_fail = 0
        for item in page_item_data:
            # 1代表请求成功
            name = '{}_{}.pdf'.format(item['title'].replace('/', '_'), item['date'].replace(' ', '&'))
            # print('name等于: ', name)
            file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", name)
            item['file_name'] = file_name
            # md5_data = self.request_duplite(file_name)
            duplicate_status = self.redis_zw.set_item('zw_cnki',file_name)
            if duplicate_status == 1:
                self.havedown_times = 0
                print('是否请求状态为: {}, 之前未请求过, 即将发起请求'.format(duplicate_status))
                flag_success = 1
                detail_url = item['detail_url']

                try:
                    res = self.session.get(detail_url, headers=headers_detail,timeout=(10,20))
                except :
                    flag_success = 0
                    for i in range(3):
                        print('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                        self.log.error('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                        time.sleep(300)
                        self.get_searchsql()
                        try:
                            res = self.session.get(detail_url, headers=headers_detail, timeout=(10, 20))
                            if res.status_code == 200 and 'pdfDown' in res.text:
                                print('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                                self.log.info('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                                flag_success = 1
                                break
                        except Exception as e:
                            flag_success = 0
                            print(repr(e))

                if flag_success == 0:
                    print('当前详情页链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
                    self.log.error('当前详情页链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
                    continue
                if res.status_code == 200 and 'pdfDown' in res.text:
                    print('detail_url 为: ',item['detail_url'])
                    print('detail_url_302为: ',res.url)
                    item['detail_url'] = res.url
                    detail_html = etree.HTML(res.text)
                    pdf_url = detail_html.xpath('//a[@id="pdfDown"][1]/@href')[0]
                    if 'javascript' not in pdf_url:
                        base_url = 'https://bar.cnki.net'
                        pdf_url_ = urljoin(base_url, pdf_url)
                        item['pdf_url'] = pdf_url_
                        print('开始下载pdf文件......')
                        items = self.download_pdf(item)
                        if items:
                            self.save(items)
                        else:
                            print('pdf文件多次请求失败, 休息10 min重新发起请求, 文件信息为: {}'.format(str(item)))
                            self.log.error('pdf文件多次请求失败, 休息10 min重新发起请求, 文件信息为: {}'.format(str(item)))
                            time.sleep(600)
                    else:
                        print('详情链接中含有javascript, 应该是需要充钱付费的, 请查看, pdf链接地址为: {}'.format(pdf_url))
                else:
                    print('详情页链接地址请求有问题, 状态不为200 或者页面内不含有pdfDown, 详情页链接地址为: {}'.format(detail_url))
            else:
                print('当前详情页以及pdf文件都已经下载过, 不再继续做处理!!!')
                self.havedown_times += 1
                if self.havedown_times < 100:
                    print('列表页中发现第 {} 次之前连续被下载过的痕迹'.format(self.havedown_times))
                    self.log.info('列表页中发现第 {} 次之前连续被下载过的痕迹'.format(self.havedown_times))
                else:
                    print('发现连续之前被下载过的详情及pdf痕迹超过100条,不再下载, 跳过本模块')
                    self.havedown_times = 0
                    return 0
        return 1

    def download_pdf(self, item):
        headers_pdf = {

            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': random.choice(useragent_pool),
            'sec-ch-ua-platform': '"Windows"',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': item['detail_url']

        }
        # print('当前的item为: ',item)

        flag_success = 1
        try:
            res = self.session.get(item['pdf_url'], headers=headers_pdf, timeout=(10,20))
            # print(dir(res.history))
        except Exception as e:
            flag_success = 0
            for i in range(3):
                print('下载pdf文件链接异常, 等待5分钟后重新登录下载, 错误显示为: {}'.format(repr(e)))
                self.log.error('下载pdf文件链接异常, 等待5分钟后重新登录下载, 错误显示为: {}'.format(repr(e)))
                time.sleep(300)
                self.get_searchsql()
                try:
                    res = self.session.get(item['pdf_url'], headers=headers_pdf, timeout=(10,20))
                    if res.status_code == 200:
                        print('pdf文件 第 {} 次尝试请求成功!!'.format(i))
                        self.log.info('pdf文件 第 {} 次尝试请求成功!!'.format(i))
                        flag_success = 1
                        break
                except Exception as e:
                    flag_success = 0
                    print(repr(e))

        if flag_success == 0:
            self.pdfdown_fail += 1
            print('当前pdf链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
            self.log.error('当前pdf链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
            return
        time.sleep(random.uniform(1, 3))
        max_limit = 51200
        if res.status_code == 200 and ('本篇支付' not in res.text) and int(res.headers['Content-Length']) > max_limit:
            self.pdfdown_fail = 0
            # with open('{}/{}.pdf'.format(self.dir_pdfs,item['title'].replace('/','_')),'wb') as f:
            #     f.write(res.content)
            # need_pay 为0 代表不需要支付
            item['need_pay'] = '无需支付'
            file_path = os.path.join(self.dir_pdfs,item['file_name'])
            pdf_obj = open(file_path, 'wb')
            pdf_obj.write(res.content)
            pdf_obj.close()
            print('下载路径地址为: {}'.format(file_path))
            print('开始识别医生信息...')
            doctor_infos = self.identify.identify_pdf(file_path)
            print('识别结果为: ',doctor_infos)
            item.update(doctor_infos)
            print("添加医生信息后的数据为: ",item)

        elif '本篇支付' in res.text or '没有订购此产品' in res.text:
            print('检测到含有本篇支付存在, 标题为: ', item['title'])
            item['need_pay'] = '需支付'
            item['doctor_info'] = ''
            item['phones'] = ''
            item['identify_status'] = '未识别'
        elif int(res.headers['Content-Length']) < max_limit:
            self.pdfdown_fail += 1
            print('注意!!当前的pdf文件小于 50 k, 重新登录并获取searchsql!!, 当前pdfdown_fail的值为: {}'.format(self.pdfdown_fail))
            self.log.info('注意!!当前的pdf文件小于 50 k, 重新登录并获取searchsql!!, 当前pdfdown_fail的值为: {}'.format(self.pdfdown_fail))
            time.sleep(5)
            self.get_searchsql()
            # self.pdfdown_fail = 0
            # for i in range(3):
            #     if self.pdfdown_fail == 0:
            #         return item
            #     else:
            #         item = self.download_pdf(item)
        else:
            print('出现了其它问题, 请注意!!')
        return item

    def save(self,item):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        item['spider_date'] = spider_date
        md5_str = item['file_name']
        # duplicate_status = self.redis_zw.set_item('zw_cnki',md5_str)
        # if duplicate_status == 1 :
        self.mongo_zw_all.insert(item)
        if ('phones' in item) and item['phones']:
            print('发现新数据, 且存在手机号, 可以插入到commit表中')
            item['commit_status'] = '未提交'
            self.mongo_zw_commit.insert(item)
        else:
            print('检测到新数据, 但手机号为空, 不加入到commit表中')
        # elif duplicate_status == 0:
        #     print('检测到重复数据, 不再加入到commit表中')
        # else:
        #     print('插入数据异常')


    def run(self):

        # (首先获取列表页session, 接着登录, 接着获取列表页获取searchsql数据)(放到一起,生成session,当cookie过期时,可重复更新获取), 接着重复遍历列表页数据, 接着根据详情页链接获取pdf数据进行保存
        # page_items = self.get_page_list()
        # for page_item_data in page_items:
        #     self.download_detail_pdf(page_item_data)
        self.get_page_list()

# 新增时的思路是: 获取数据库最大的日期与对应的title,锁定到具体在第几页, 然后倒着去获取数据
# queryjson里面的name决定了大块的搜索范围, 如: 参考文献: 临床医学: RF  作者单位: 医院: AF, 可以请求 https://piccache.cnki.net/2022/kdn/index/kns8/nvsmscripts/min/fieldjson.min.js?v=1.6获取对应的json标记