import copy
import json
import random
import re
import time
from datetime import datetime
from urllib.parse import quote
from lxml import etree
from ..login_tsg90 import LoginTrun
from ..cx_mongo import CxMongo
from ..redis_cx import CxRedis
from ..cur_identify import CurIdentify
from urllib.parse import urljoin
from .get_chaoxing_moudle import get_moudles

class ChaoXing():

    def __init__(self):

        self.spider_at = 'linux'
        self.owning_account = '6849_超星1'
        # self.search_info['platform'] = '作者单位'
        self.identify = CurIdentify()
        self.login_obj = LoginTrun(self.owning_account)
        self.session = self.login_obj.login_page_turn(self.owning_account)
        # self.search_keywords = '糖尿病'
        # self.search_keywords = '细胞'
        self.tasks_path = './task/chaoxing/chaoxing_config_2015_2016.json'
        self.dir_pdfs = 'F:/chaoxing_pdfs'
        self.cx_mongo_all = CxMongo('wfhy_update', 'chaoxing_all')
        self.cx_mongo_commit = CxMongo('wfhy_commit', 'chaoxing_commit')
        self.redis_cx = CxRedis()
        self.redis_all_phones = CxRedis()
        # item 用于存储每篇文章的目标信息, 最后存入到数据库
        self.item = {}
        self.retry_down_list_max = 10
        self.list_fail_num = 0
        self.have_spider_num = 0
        self.have_spider_num_max = 255
        self.turn_page_num = 5
        self.get_detailfail_num = 0


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

    def error_handle(self,html):

        if '校外远程访问系统' in html:
            print('出现 校外远程访问系统 , 休息一会儿, 重新登录后继续请求!!')
            self.login_again()
        elif '内部服务器错误' in html:
            print('出现内部服务器错误字样, vpn 不太稳定, 暂停 10~15min, 重新登录, 再次获取数据!!')
            time.sleep(random.uniform(600,900))
            self.login_again()
        elif '登录失效' in html:
            print('当前页面出现登录失效, 休息3~5min, 重新登录后继续获取!!')
            time.sleep(random.uniform(180, 300))
            self.login_again()
        elif '找不到和您的查询相符的资源' in html:
            print('检索关键字有问题, 没有查到相关的资源, 退出!!')
            exit()
        elif '请重新进入21' in html:
            print('检测到 请重新进入21 字样, 休息2min, 重新登录获取数据!!')
            time.sleep(120)
            self.login_again()

        with open('chaoxingerror.html', 'w', encoding='utf-8') as f:
            f.write(html)
            f.close()

    def request_page_num(self):

        url_adv_param = "(O='" + self.search_info['keywords'] + "')"
        quote_param = quote(url_adv_param)
        list_url = "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw={}&strkey={}&strmag={}&stryear={}&strclassfy=16_-1&topsearch=4&adv=JN{}&aorp=a&nosim=1&size={}&isort=3&x=0_230&pages=1".format(
            quote(self.search_info['keywords']), self.second_value, self.three_value, self.years_match[self.cur_year],
            quote_param, self.search_info['page_size'])
        # list_url = "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw=%E5%8C%BB%E9%99%A2&stryear=9&topsearch=4&adv=JN%28O%3D%27%E5%8C%BB%E9%99%A2%27%29&aorp=a&nosim=1&size=50&isort=3&x=0_230&pages=1"
        print('列表页连接地址为: {}'.format(list_url))
        header_list = {
            "Host": "nmg.jitui.me",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw={}&strkey={}&strmag={}&stryear={}&strclassfy=16_-1&topsearch=4&adv=JN{}&aorp=a&nosim=1&size={}&isort=3&x=0_230&pages=1".format(
            quote(self.search_info['keywords']), self.second_value, self.three_value, self.years_match[self.cur_year],
            quote_param, self.search_info['page_size']),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cookie": "ishide=true; clientId=CIDfbcb39db24a7fc2d728669bbbab25c50; JSESSIONID=B6DAFBC660302330DC6A9B54090BE3CD; ddhgguuy_session=4vish9ut10t0qbn16eh372af05"
        }

        for i in range(self.retry_down_list_max):
            # try:
            time.sleep(random.uniform(2, 5))
            try:
                res = self.session.get(list_url, headers=header_list, timeout=(20, 30))
            except Exception as e:
                print('获取get_num时, 请求列表页出现异常, 详情为: {} ,休息一下, 重新获取列表页数据!!'.format(repr(e)))
                time.sleep(random.uniform(30, 60))
                if i > 3:
                    print('获取get_num连续出现3次以上错误, 重新登录获取数据!!')
                    self.login_again()
                continue
            res.encoding = 'utf-8'
            html = etree.HTML(res.text)
            total_data = html.xpath('//div[@class="oringinalBox"]/span/text()')
            if res.status_code == 200 and total_data:
                total_num = int(total_data[0].replace(',',''))
                new_page_num = total_num // self.search_info['page_size'] + 1
                print('当前模块共 {} 条, 预估含有文章 {} 页'.format(total_num,new_page_num))
                return total_num,new_page_num
            else:
                if i >= 5:
                    print("超过5次获取列表页总页码失败, 暂停30~40min重新获取, 重新登录获取!!".format(i))
                    self.login_again()
                    time.sleep(random.uniform(1800, 2400))
                else:
                    print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                    time.sleep(random.uniform(5, 10))
                self.error_handle(res.text)


    def get_page_num(self):
        '''
        获取最新搜索数据的最大页码, 与数据库中搜索数据最大页码做比较, 如果前者大于后者说明之前未抓取完成, 将数据库的最大页码作为待抓取的开始抓取页进行抓取,反之, 说明当前年已经抓取完成, 直接进入下一年进行数据抓取
        :param year: 当前列表页所属年份
        :return: 待抓取数据的最大及最小页码
        '''

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
        # if self.cur_year >= 2023:
        sql_page_data = self.find_mongo_page()
        if sql_page_data == 0:
            total_num, new_page_num = self.request_page_num()
            print('当前模块数据未抓取过, 从最大页码开始抓取, 最大页为网站总页码: {}, 结束页码为: 0'.format(new_page_num))
            min_page = 0
            max_page = new_page_num
            if total_num == 0:
                print('该模块之前未抓取过, 但本身的项目条数为0, 不抓取!!')
                self.item['phones'] = ''
                self.item['owning_account'] = self.owning_account
                self.item['cur_year'] = self.cur_year
                self.item['cur_page'] = 1
                self.item['type'] = '当前模块数据为空'
                self.save()
        else:
            sql_min_page = sql_page_data[0][0]
            sql_max_page = sql_page_data[0][1]
            cur_moudle_sql_total = sql_page_data[1]
            print('检测到数据库中最大页码为:{}, 最小页码为: {}'.format(sql_max_page, sql_min_page))
            if self.cur_year >= 2023:
                # 如果为2023年数据,当数据库中存在第一页时需要查看最大页码与网页中最大页码之间的值, 如果有间隔说面有更新
                total_num, new_page_num = self.request_page_num()
                if sql_min_page == 1:
                    print('数据库中最小页码为1,说明之前已经抓取过一遍数据')
                    if sql_max_page < new_page_num:
                        max_page = new_page_num - sql_max_page
                        min_page = 0
                        print('之前已经抓取过全部的一遍数据,目前网站新增数据 {} 页,接下来我们从第 {} 页倒着抓取!!'.format(max_page, max_page))
                    elif total_num - cur_moudle_sql_total > 10:
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
                    max_page = new_page_num - sql_max_page + sql_min_page
                    min_page = 0
            else:
                if sql_min_page == 1:
                    print('数据库中最小页码为1,说明之前已经抓取过一遍数据')
                    print('当前模块当前模块已经抓取完成, 进入下一模块!!')
                    return 'cur_moudle_have_spider'
                else:
                    print('数据库中最小页码为{}, 大于1 , 说明之前数据还未完全抓取完成, 接下来继续抓取!!'.format(sql_min_page))
                    time.sleep(2)
                    total_num, new_page_num = self.request_page_num()
                    max_page = new_page_num - sql_max_page + sql_min_page
                    min_page = 0
        return min_page, max_page


    def find_mongo_page(self):
        '''
        根据账号和origin_moudle信息锁定待抓取当前年之前已经抓取过保存在数据库中的最大的页面
        :return:
        '''

        sql_page = self.cx_mongo_all.find_page_num(self.owning_account, self.item['origin_moudle'])
        return sql_page

    def get_detail(self):

        headers = {
                "Host": "nmg.jitui.me",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                # "Cookie": "ishide=true; JSESSIONID=C9CF6A0F4857BC730F63725C9634613A; ddhgguuy_session=ss2v2dofr4ghirilr5ppe787m0",
                "Referer": "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw=%E5%8C%BB%E9%99%A2&topsearch=4&adv=JN%28O%3D%27%E5%8C%BB%E9%99%A2%27%29&aorp=a&nosim=1&size=50&x=0_230&pages=1"
            }
        for i in range(3):
            try:
                res = self.session.get(self.item['detail_url'],headers=headers,timeout=(20,30))
                time.sleep(random.uniform(0.5,1))
            except Exception as e:
                print('详情页下载异常, 详情为: {}, 再次发起请求!!'.format(repr(e)))
                continue

            if res.status_code == 200 and '阅读全文' in res.text:
                self.get_detailfail_num = 0
                html = etree.HTML(res.text)
                author_infos = html.xpath('//p[@data-meta-name="作者简介"]/text()')
                if author_infos:
                    author_info = author_infos[0].strip()
                else:
                    print('当前没有作者简介!! 连接地址为: {}'.format(self.item['detail_url']))
                    author_info = ''
                communi_authors = html.xpath('//p[@data-meta-name="通信作者"]/text()')
                if communi_authors:
                    communi_author = communi_authors[0].strip()
                else:
                    print('当前没有通信作者信息!! 连接地址为: {}'.format(self.item['detail_url']))
                    communi_author = ''
                self.item['doctor_info'] = author_info + communi_author
                if self.item['doctor_info']:
                    phones = re.findall('(1[35678]\d{9})', self.item['doctor_info'])
                    if phones:
                        print('疑似手机号为: ', re.findall('(1[35678]\d{9})', self.item['doctor_info']))
                        self.item['phones'] = []
                        # print('这是phones数据: ',phones)
                        for phone in phones:
                            if len(phone) == 11:
                                print('恭喜你! 发现真实手机号一枚: {}'.format(phone))
                                # self.log.info('恭喜你! 发现真实手机号一枚: {} 文件路径为: {}'.format(phone,file_path))
                                self.item['phones'].append(phone)
                            else:
                                print('识别出号码长度过长, 为 {} 位, 确认不是真手机号, 舍去!!'.format(len(phone)))
                                self.item['phones'] = ''
                    else:
                        self.item['phones'] = ''
                else:
                    print('详情业内没有任何关于作者的详情信息!!')
                    self.item['phones'] = ''
                break
            else:
                print('详情页请求失败, 休息一下, 重新发起请求!!')
                with open('chaoxingdetailerror.html','w',encoding='utf-8') as f:
                    f.write(res.text)
                    f.close()
                time.sleep(random.uniform(5,8))

        else:
            if 'phones' not in self.item:
                self.item['phones'] = ''
            if 'doctor_info' not in self.item:
                self.item['doctor_info'] = ''
            # print('下载pdf文件连续出错第 {} 次, 休息一下, Go on!!!'.format(self.down_pdffail_num))
            self.get_detailfail_num += 1
            time.sleep(random.uniform(1, 3))
        if self.get_detailfail_num >= 10:
            print('连续 30 个pdf文件下载失败, 可能遇到反爬, 休息2~3分钟后, 重新登录一下, 继续抓取!!'.format(self.turn_page_num))
            time.sleep(random.uniform(120, 180))
            self.login_again()

    def get_page_list(self):

        url_adv_param = "(O='" + self.search_info['keywords'] + "')"
        quote_param = quote(url_adv_param)
        list_url = "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw={}&strkey={}&strmag={}&stryear={}&strclassfy=16_-1&topsearch=4&adv=JN{}&aorp=a&nosim=1&size={}&isort=3&x=0_230&pages={}".format(
            quote(self.search_info['keywords']), self.second_value,self.three_value,self.years_match[self.cur_year], quote_param,self.search_info['page_size'],self.cur_page)
        # list_url = "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw=%E5%8C%BB%E9%99%A2&stryear=9&topsearch=4&adv=JN%28O%3D%27%E5%8C%BB%E9%99%A2%27%29&aorp=a&nosim=1&size=50&isort=3&x=0_230&pages=1"
        print('列表页连接地址为: {}'.format(list_url))
        header_list = {
                "Host": "nmg.jitui.me",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Referer": "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw=%E5%8C%BB%E9%99%A2&strkey=209&strmag=429007&stryear=8&strclassfy=16_-1&topsearch=4&adv=JN%28O%3D%27%E5%8C%BB%E9%99%A2%27%29&aorp=a&nosim=1&size=50&isort=3&x=0_230&pages=2",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                # "Cookie": "ishide=true; clientId=CIDfbcb39db24a7fc2d728669bbbab25c50; JSESSIONID=B6DAFBC660302330DC6A9B54090BE3CD; ddhgguuy_session=4vish9ut10t0qbn16eh372af05"
            }

        for i in range(self.retry_down_list_max):
            # print('这是列表url: ', list_url)
            # print('这是headers: ',header_list)
            # print('这是cookies: ',self.session.cookies)
            time.sleep(random.uniform(2, 5))
            try:
                res = self.session.get(list_url, headers=header_list, timeout=(20, 30))
            except Exception as e:
                print('请求列表页出现异常, 详情为: {} 休息一下, 重新获取列表页数据!!'.format(repr(e)))
                time.sleep(random.uniform(30, 60))
                if i >= 2:
                    print('列表页获取出现异常连续超过2次, 重新登录获取!!')
                    self.login_again()
                continue
            res.encoding = 'utf-8'
            if res.status_code == 200 and '发表时间' in res.text:
                html = etree.HTML(res.text)
                trs = html.xpath('//table[@class="listTable"]/tbody/tr')
                # 直接那详情页数据,并识别里面的电话号码, 因为html数据与pdf文件里面的数据是一致 的
                if len(trs) > 0:
                    for tr in trs:
                        self.item.clear()
                        tds = tr.xpath('./td')
                        print('***' * 20)
                        self.item['owning_account'] = self.owning_account
                        self.item['title'] = tds[1].xpath('./a/@title')[0].strip()
                        detail_url = tds[1].xpath('./a/@href')

                        if detail_url:
                            self.item['detail_url'] = urljoin('http://nmg.jitui.me/',detail_url[0])
                            self.item['date'] = tds[5].xpath('./span/text()')[0].strip()
                            self.item['file_name'] = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                                            self.item['title']) + '_' + self.item['date']
                            status = self.redis_cx.set_item('chaoxing', self.item['file_name'])
                            if status == 1:
                                self.have_spider_num = 0
                                file_path = self.dir_pdfs + '/' + self.item['file_name']
                                authors_data = tds[2].xpath('./text()')
                                if authors_data:
                                    authors = authors_data[0].strip()
                                else:
                                    authors = ''
                                self.item['author'] = authors

                                try:
                                    self.item['origin'] = tds[3].xpath('./a/text()')[0].strip()
                                except:
                                    self.item['origin'] = '不详'
                                try:
                                    self.item['lanmu'] = tds[4].xpath('./span/text()')[0].strip()
                                except:
                                    self.item['lanmu'] = '不详'
                                self.item['type'] = tds[6].xpath('./span/text()')[0].strip()
                                self.item['read_num'] = tds[8].xpath('./span/text()')[0].strip()
                                self.item['cur_page'] = self.cur_page
                                self.item['cur_year'] = self.cur_year

                                self.item['origin_moudle'] = '{}_{}_{}_{}_{}'.format(self.search_info['platform'],
                                                                                     self.search_info['keywords'],
                                                                                     self.cur_year, self.second_name,
                                                                                     self.three_name)

                                self.get_detail()
                                print(self.item)
                                self.save()
                            else:
                                print('当前项目数据已经抓取过, 跳过!!!')
                                self.have_spider_num += 1
                                print('连续抓取过数据第 {} 个, 继续抓取, 跳过!'.format(self.have_spider_num))
                                if self.have_spider_num > self.have_spider_num_max:
                                    print('连续抓取过数据超过 {} 个, 向后跳 {} 页, 继续抓取!'.format(self.have_spider_num_max,
                                                                                   self.turn_page_num))
                                    self.cur_page -= self.turn_page_num
                                    self.have_spider_num = 0
                                    return 'turn_over'
                            print('***'*20)
                        else:
                            print('没有获取到详情页连接地址, 当前项目跳过!!')
                            continue
                        # print('详情链接地址为: {}'.format(detail_url))
                    break
                else:

                    print('当前列表页没有项目数据,连接地址为: {}'.format(list_url))
                    break
            else:
                print('没有获取到当前列表页数据,休息一下5~8min,重新获取!!')

                time.sleep(random.uniform(5, 10))
                if i >= 2:
                    print('列表页连续大于2次没有获取到数据, 等待10~20min重新登录获取数据!!')
                    time.sleep(random.uniform(600, 1200))
                    self.login_again()



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
                    self.cx_mongo_all.insert(phones)
                    # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                    duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf',phone)
                    if duplicate_status == 1:
                        phones['commit_status'] = '未提交'
                        self.cx_mongo_commit.insert(phones)
                        print('发现的手机号已插入 commit 表中!!!')

                    else:
                        print('跳过当前手机号!! 不再放入 commit 表中')
            else:
                self.item['phones'] = self.item['phones'][0]
                self.cx_mongo_all.insert(self.item)
                # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf', self.item['phones'])
                if duplicate_status == 1:
                    self.item['commit_status'] = '未提交'
                    self.cx_mongo_commit.insert(self.item)
                    print('发现的手机号已插入 commit 表中!!!')

                else:
                    print('跳过当前手机号!! 不再放入 commit 表中')
        else:
            print('发现新数据, 但没有手机号, 将手机号重置为空, 放入chaoxing_all中')
            self.item['phones'] = ''
            self.cx_mongo_all.insert(self.item)
        self.item.clear()


    def run(self):
        # print(self.session.cookies)
        self.years_match = {2023:7,2022:8,2021:9,2020:10,2019:11,2018:12,2017:13,2016:14,2015:15}
        for i in range(3):
            # try:
            # 获取待抓取任务的排序信息
            self.get_search_info()
            # 排队执行所有待抓取的任务
            for search_info in self.search_infos:
                self.search_info = search_info
                print('当前在抓取的任务信息为: ', self.search_info)
                time.sleep(5)
                for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):
                    self.cur_year = year
                    second_moudles,three_moudles = get_moudles()
                    for second_name,second_value in second_moudles.items():
                        for three_name,three_value in three_moudles.items():
                            self.second_name = second_name
                            self.second_value = second_value
                            self.three_name = three_name
                            self.three_value = three_value
                            self.item['origin_moudle'] = '{}_{}_{}_{}_{}'.format(self.search_info['platform'],
                                                                               self.search_info['keywords'],
                                                                               self.cur_year,second_name,three_name)
                            print('当前是 {} 年, 基本信息为: {},模块为: {}'.format(self.cur_year, str(self.search_info),self.item['origin_moudle']))
                            self.update_task(self.search_info, have_start=1, is_running=1, cur_year=self.cur_year)

                            data = self.get_page_num()
                            if data != 'cur_moudle_have_spider':
                                # 进入新的一年后, 将已经抓去过数据数量设置为 0
                                min_page, max_page = data
                                self.cur_page = max_page
                                while self.cur_page > min_page:
                                    print(
                                        '当前是{} {} {} {}年{}{} 第 {} 页数据'.format(self.owning_account, self.search_info['platform'],
                                                                          self.search_info['keywords'], year,
                                                                          second_name,three_name,self.cur_page))
                                    spider_status = self.get_page_list()
                                    if spider_status == 'turn_over':
                                        print('检测到当前发生了页面跳过, 跳转之后的页码为: {}'.format(self.cur_page))
                                        time.sleep(random.uniform(2, 5))
                                    elif spider_status == 'moudle_done':
                                        print('当前模块已经没有数据可抓取,开始抓取下一个模块!!')
                                        break
                                    self.cur_page -= 1
                            else:
                                print('开始抓取下一个模块数据!')
                            # self.update_task(self.search_info, have_start=0, have_end=0,is_running=0, cur_year=self.cur_year)
                self.update_task(self.search_info, have_end=1, is_running=0, cur_year=self.cur_year)
            break
            # except Exception as e:
            #     print('抓取时出现问题, 休息10~15分钟, 详情为: {}'.format(repr(e)))
            #     time.sleep(random.uniform(600, 900))
            #     self.update_task(self.search_info, is_running=0, cur_year=self.cur_year)
            #     time.sleep(random.uniform(5,10))


