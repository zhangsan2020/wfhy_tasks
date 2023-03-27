import copy
import json
import random
import re
import time
from datetime import datetime
from urllib.parse import quote
from lxml import etree
from task.chinesejournal.cur_identify import CurIdentify
from task.common.login_tsg90 import LoginTrun
from ..sw_mongo import SwMongo
from task.china_sw.redis_sw import SwRedis
from ..cur_identify import CurIdentify


class ChinaSw():

    def __init__(self):

        self.spider_at = 'win'
        self.owning_account = '6849_中国生物_'
        # self.search_info['platform'] = '作者单位'
        self.identify = CurIdentify()
        self.login_obj = LoginTrun(self.owning_account)
        self.session = self.login_obj.login_page_turn(self.owning_account)
        # self.search_keywords = '糖尿病'
        # self.search_keywords = '细胞'
        self.domain = 'www-sinomed-ac-cn.njmu.hknsspj.cn'
        self.tasks_path = './task/china_sw/chinasw_config.json'
        self.dir_pdfs = 'F:/chinasw_pdfs'
        self.sw_mongo_all = SwMongo('wfhy_update', 'chinasw_all')
        self.sw_mongo_commit = SwMongo('wfhy_commit', 'chinasw_commit')
        self.redis_sw = SwRedis()
        self.redis_all_phones = SwRedis()
        # item 用于存储每篇文章的目标信息, 最后存入到数据库
        self.item = {}
        self.retry_down_pdf_max = 3
        self.retry_down_list_max = 10
        self.down_pdffail_num = 0
        self.list_fail_num = 0
        self.have_spider_num = 0
        self.have_spider_num_max = 255
        self.turn_page_num = 5
        self.identify_failed = 0
        self.identify_failed_limit = 52
        self.get_pdf_url_failed = 0

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
        list_url = 'http://{}/crossSearch.do?sf_request_type=ajax'.format(self.domain)
        data = {
            "sql": "AD_ALL/1='{}' AND DP_YEAR/1='{}'".format(self.search_info['keywords'], self.cur_year),
            "dbs":"zh,en,lw,kp",
            "db":"zh",
            "pageNo": "1",
            "pageSize": self.search_info['page_size'],
            "ajax": "items",
            "searchword": "(\"{}\"[{}]) AND (\"{}\"[时间]) ".format(self.search_info['keywords'],
                                                                  self.search_info['platform'], self.cur_year),
            "cmode": "tl",
            "orderBy": "LIFO",
            "flag": "true",
            "selected": "undefined",
            "hType":""
        }
        header_list = {
                        # "Host": "{}".format(self.domain),
                        "Connection": "keep-alive",
                        "Content-Length": "307",
                        "Accept": "text/html, */*",
                        "X-Requested-With": "XMLHttpRequest",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Origin": "http://{}".format(self.domain),
                        "Referer": "http://{}/crossSearch.do?searchwordwm={}{}".format(self.domain,
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
            with open('生物更新.html','w',encoding='utf-8') as f:
                f.write(res.text)
                f.close()
            max_page_data = re.findall('共(\d+)页', res.text)
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
        sql_page = self.sw_mongo_all.find_sw_page_num(self.item['origin_moudle'])
        return sql_page

    def get_page_list(self):

        list_url = 'http://{}/crossSearch.do?sf_request_type=ajax'.format(self.domain)
        data = {
            "sql": "AD_ALL/1='{}' AND DP_YEAR/1='{}'".format(self.search_info['keywords'], self.cur_year),
            "dbs": "zh,en,lw,kp",
            "db": "zh",
            "pageNo": "{}".format(self.cur_page),
            "pageSize": self.search_info['page_size'],
            "ajax": "items",
            "searchword": "(\"{}\"[{}]) AND (\"{}\"[时间]) ".format(self.search_info['keywords'],
                                                                  self.search_info['platform'], self.cur_year),
            "cmode": "tl",
            "orderBy": "LIFO",
            "flag": "true",
            "selected": "undefined",
            "hType": ""
        }
        header_list = {
            "Host": "{}".format(self.domain),
            "Connection": "keep-alive",
            "Content-Length": "307",
            "Accept": "text/html, */*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "{}".format(self.domain),
            "Referer": "http://{}/crossSearch.do?searchwordwm={}{}".format(self.domain,
                quote(self.search_info['keywords']), quote(self.search_info['platform'])),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        for i in range(self.retry_down_list_max):

            time.sleep(random.uniform(2, 5))
            try:
                res = self.session.post(list_url, data=data, headers=header_list, timeout=(20, 30))
            except Exception as e:
                print('请求列表页出现异常, 详情为: {} 休息一下, 重新获取列表页数据!!'.format(repr(e)))
                time.sleep(random.uniform(30, 60))
                continue
            res.encoding = 'utf-8'
            if res.status_code == 200:
                html = etree.HTML(res.text)
                divs = html.xpath('//div[@class="right-wztxt fL"]')
                if len(divs) > 0:
                    for div in divs:
                        self.item.clear()
                        try:
                            pdf_flag = div.xpath('./h2/span/a/img/@src')
                            print('***' * 20)
                            if pdf_flag and 'pdf.jpg' in pdf_flag[0].strip():
                                print('存在pdf文件下载')
                                self.item['owning_account'] = self.owning_account
                                self.item['title'] = div.xpath('./h2/input/@value')[0].strip()
                                self.item['detail_id'] = div.xpath('./h2/input/@id')[0].strip().split('_')[0]
                                self.item['file_name'] = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                                                self.item['title']) + '_' + self.item['detail_id'] + '.pdf'
                                # md5_str = self.item['file_name'] + '_' + self.item['date'] + '.pdf'

                                status = self.redis_sw.set_item('chinasw', self.item['file_name'])
                                if status == 1:
                                    self.have_spider_num = 0
                                    file_path = self.dir_pdfs + '/' + self.item['file_name']

                                    # self.item['author'] = div.xpath('./p[1]/b')[0].xpath('string(.)').strip()
                                    self.item['item_id'] = int(div.xpath('./div/input[1]/@id')[0].strip())
                                    authors_data = div.xpath('./p[1]/b/a/text()')
                                    authors = []
                                    if authors_data:
                                        for author_data in authors_data:
                                            author = author_data.strip().split('(')[0]
                                            authors.append(author)
                                    self.item['author'] = json.dumps(authors, ensure_ascii=False)
                                    try:
                                        self.item['unit'] = div.xpath('./p[2]/font/text()')[0].strip()
                                    except:
                                        self.item['unit'] = '不详'
                                    try:
                                        self.item['origin'] = div.xpath('./p[3]/a[1]/text()')[0].strip()
                                    except:
                                        self.item['origin'] = '不详'
                                    # http://www-sinomed-ac-cn.njmu.hknsspj.cn/index.jsp/zh/detail.do?ui=2023103671
                                    self.item['detail_url'] = 'http://{}{}'.format(self.domain,div.xpath('./h2/a/@href')[0].strip())
                                    print('这是详情页连接地址: ',self.item['detail_url'])
                                    self.item['pdf_url'] = self.get_pdf_url(self.item['title'], self.item['detail_id'])
                                    self.item['cur_page'] = self.cur_page
                                    self.item['cur_year'] = self.cur_year
                                    self.item['origin_moudle'] = '{}_{}_{}年'.format(self.search_info['platform'],
                                                                                       self.search_info['keywords'],
                                                                                       self.cur_year)
                                    if not self.item['pdf_url']:
                                        self.item['identify_status'] = 'pdf连接地址获取失败'
                                        print('pdf 连接地址获取失败,跳过当前item!!')
                                        continue
                                    self.down_pdf(file_path)
                                    print('下载路径地址为: {}'.format(file_path))
                                    print('开始识别医生信息...')
                                    doctor_infos = self.identify.identify_pdf(file_path)
                                    print('识别结果为: ', doctor_infos)
                                    # if doctor_infos['identify_status'] == '识别失败':
                                    #     self.identify_failed += 1
                                    #     print('当前是连续第 {} 次识别pdf文件失败!'.format(self.identify_failed))
                                    #     if self.identify_failed > self.identify_failed_limit:
                                    #         print('连续超过 {} 次识别pdf文件失败, 可能遇到了反爬, 等待1~2min, 重新登录一下!!'.format(
                                    #             self.identify_failed_limit))
                                    #         time.sleep(random.uniform(60, 120))
                                    #         self.login_again()
                                    #         self.identify_failed = 0
                                    # else:
                                    #     self.identify_failed = 0
                                    self.item.update(doctor_infos)
                                    print("添加医生信息后的数据为: ", self.item)
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
                                print('当前item不存在pdf文件下载, 跳过!!')
                                continue
                        except Exception as e:
                            print('当前项目获取时出现异常, 详情为: {}, 直接进行下个项目获取!!'.format(repr(e)))
                            continue
                    break
                else:
                    print('没有获取到当前列表页数据,休息一下5~8min,重新获取!!')
                    time.sleep(random.uniform(300, 480))
            else:
                if i >= 5:
                    print('列表页连续大于5次没有获取到数据, 等待30~40min重新登录获取数据!!')
                    self.login_again()
                    time.sleep(random.uniform(1800, 2400))
                elif i >=2 and i< 5:
                    print("超过2次获取列表页数据失败, 暂停5~10min重新获取, 重新登录获取!!".format(i))
                    self.login_again()
                    time.sleep(random.uniform(300, 600))
                else:
                    print("第 {} 次获取列表页总页码失败, 休息一会儿, 重新获取!!".format(i))
                    time.sleep(random.uniform(10, 20))

    def down_pdf(self, file_path):

        for i in range(self.retry_down_pdf_max):
            headers_pdf = {
                    # "Host": "pdf-juhe-com-cn.njmu.fg77.club",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "Referer": "http://{}/".format(self.domain),
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
            print('开始下载pdf文件...')
            # print('cookie为: ', self.session.cookies.get_dict())
            try:
                r = self.session.get(self.item['pdf_url'], headers=headers_pdf, timeout=(30, 60))
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print('下载pdf文件时, 出现程序错误, 详情为: {}, 休息一下, 继续执行'.format(repr(e)))
                time.sleep(random.uniform(5,10))
                continue
            if r.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(r.content)
                    f.close()
                print('成功下载pdf文件!!')
                self.down_pdffail_num = 0
                break
            else:
                print('下载pdf文件时状态码异常!! 重新下载')
                time.sleep(random.uniform(2, 5))
                self.down_pdffail_num += 1
                if self.down_pdffail_num >= 15:
                    print('pdf下载出错超过15次, 等待3~5分钟, 重新开始下载数据!!')
                    time.sleep(random.uniform(180, 300))
                    self.down_pdffail_num = 0
        else:
            print('下载pdf文件连续出错第 {} 次, 休息一下, Go on!!!'.format(self.down_pdffail_num))
            self.down_pdffail_num += 1
            time.sleep(random.uniform(1, 3))
        if self.down_pdffail_num >= 30:
            print('连续 30 个pdf文件下载失败, 可能遇到反爬, 休息2~3分钟后, 向后跳 {} 页, 继续抓取!!'.format(self.turn_page_num))
            time.sleep(random.uniform(120, 180))
            # self.login_again()
            self.cur_page -= self.turn_page_num
            self.down_pdffail_num = 0
            return 'turn_over'

    def get_pdf_url(self, ti, id_):

        url = 'http://{}/zh/relatedLink.do?method=pdfLink&sf_request_type=ajax'.format(self.domain)
        data = {
            "id": id_,
            "ti": ti,
            "db": "zh_pdf"
        }
        headers = {
                "Host": "{}".format(self.domain),
                "Connection": "keep-alive",
                "Content-Length": "297",
                "Accept": "text/plain, */*",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://{}".format(self.domain),
                # "Referer": "http://www-sinomed-ac-cn.njmu.hknsspj.cn/crossSearch.do?searchwordwm=%E5%8C%BB%E9%99%A2%E4%BD%9C%E8%80%85%E5%8D%95%E4%BD%8D",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }

        for i in range(3):
            try:
                res = self.session.post(url, data=data, headers=headers, timeout=(20, 30))
                print(res.text)
                time.sleep(random.uniform(0.5,1))
                if res.status_code == 200 and 'CBMDownPaper.ashx?Path' in res.text:
                    self.get_pdf_url_failed = 0
                    pdf_url = re.findall('href="(.*?)"', res.text)[0].strip()
                    print('成功获取到pdf连接地址为: {}'.format(pdf_url))
                    return pdf_url
                elif '请重新进入' in res.text:
                    print('重新登录一下, 再次进行下载!!')
                    time.sleep(random.uniform(30,60))
                    self.login_again()
                else:
                    print('第 {} 次pdf连接地址获取失败, 等待一下重新获取'.format(i))
                    time.sleep(random.uniform(1, 2))
                    self.get_pdf_url_failed += 1
                    if self.get_pdf_url_failed >= 15:
                        print('连续获取pdf连接地址失败超过15次,休息3~5 分钟, 重新获取!!')
                        time.sleep(random.uniform(180,300))
                        self.login_again()
                        self.get_pdf_url_failed = 0
            except:
                print('第 {} 次pdf连接地址获取时读取失败或请求出错,不打紧再来!!'.format(i))
                time.sleep(random.uniform(1, 3))
                if i >= 1:
                    print('第 {} 次pdf连接地址是程序异常, 等待一下3~5min,重新获取'.format(i))
                    time.sleep(random.uniform(180, 300))
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
                    self.sw_mongo_all.insert(phones)
                    # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                    duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf',phone)
                    if duplicate_status == 1:
                        phones['commit_status'] = '未提交'
                        self.sw_mongo_commit.insert(phones)
                        print('发现的手机号已插入 commit 表中!!!')

                    else:
                        print('跳过当前手机号!! 不再放入 commit 表中')
            else:
                self.item['phones'] = self.item['phones'][0]
                self.sw_mongo_all.insert(self.item)
                # 去重状态,目的是去除重复的手机号, 存储在commit中的一定是之前没有见过的新手机号,最终给到销售
                duplicate_status = self.redis_all_phones.insert_phone('all_phones_pdf', self.item['phones'])
                if duplicate_status == 1:
                    self.item['commit_status'] = '未提交'
                    self.sw_mongo_commit.insert(self.item)
                    print('发现的手机号已插入 commit 表中!!!')

                else:
                    print('跳过当前手机号!! 不再放入 commit 表中')
        else:
            print('发现新数据, 但没有手机号, 将手机号重置为空, 放入sw_mongo_all中')
            self.item['phones'] = ''
            self.sw_mongo_all.insert(self.item)
        self.item.clear()


    def run(self):
        # print(self.session.cookies)
        for i in range(3):
            try:
                # 获取待抓取任务的排序信息
                self.get_search_info()
                # 排队执行所有待抓取的任务
                for search_info in self.search_infos:
                    self.search_info = search_info
                    print('当前在抓取的任务信息为: ', self.search_info)
                    time.sleep(5)
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
                break
            except Exception as e:
                print('抓取时出现问题, 休息10~15分钟, 详情为: {}'.format(repr(e)))
                print(f'error file:{e.__traceback__.tb_frame.f_globals["__file__"]}')
                print(f"error line:{e.__traceback__.tb_lineno}")
                time.sleep(random.uniform(600, 900))
                self.update_task(self.search_info, is_running=0, cur_year=self.cur_year)
                time.sleep(random.uniform(5,10))


