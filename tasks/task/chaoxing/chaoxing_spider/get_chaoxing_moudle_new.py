#!/usr/bin/python3
import json
import random
import time
from urllib.parse import quote
from lxml import etree
from task.common.login_tsg90 import LoginTrun

class ChaoXingMoudle():

    def __init__(self,owning_account,domain):

        self.spider_at = 'win'
        self.owning_account = owning_account
        self.domain = domain
        # self.search_info['platform'] = '作者单位'
        self.login_obj = LoginTrun(self.owning_account)
        self.session = self.login_obj.login_page_turn(self.owning_account)
        # self.search_keywords = '糖尿病'
        # self.search_keywords = '细胞'
        self.tasks_path = './task/chaoxing/chaoxing_config_second.json'
        self.dir_pdfs = 'F:/chaoxing_pdfs'
        self.retry_down_list_max = 10
        self.second_moudles = {}

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


    def get_moudle_infos(self):

        url_adv_param = "(O='" + self.search_info['keywords'] + "')"
        quote_param = quote(url_adv_param)
        # 机构:
        # 主题:
        list_url = "http://{}/searchjour?sw={}&stryear={}&strclassfy=16_-1&topsearch=4&adv=JN{}&aorp=a&nosim=1&size={}&isort=3&x=0_63".format(
            self.domain,quote(self.search_info['keywords']), self.years_match[self.cur_year], quote_param,self.search_info['page_size'])
        # list_url = "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/searchjour?sw=%E5%8C%BB%E9%99%A2&stryear=9&topsearch=4&adv=JN%28O%3D%27%E5%8C%BB%E9%99%A2%27%29&aorp=a&nosim=1&size=50&isort=3&x=0_230&pages=1"
        print('列表页连接地址为: {}'.format(list_url))
        header_list = {
                "Host": self.domain,
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Referer": "http://{}/searchjour?sw={}&stryear={}&strclassfy=16_-1&topsearch=4&adv=JN{}&aorp=a&nosim=1&size={}&isort=3&x=0_63".format(
            self.domain,quote(self.search_info['keywords']), self.years_match[self.cur_year], quote_param,self.search_info['page_size']),
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9"
            }

        for i in range(self.retry_down_list_max):
            print('这是列表url: ', list_url)
            print('这是headers: ',header_list)
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
                keywords_div = html.xpath('//div[@name="keywords"]')
                for div in keywords_div:
                    # print(div)
                    name = div.xpath('.//font/@title')[0].strip()
                    value = div.xpath('./@value')[0].strip()
                    total_data = div.xpath('.//font[1]/following-sibling::span[1]/text()')[0].strip()
                    if name and value and total_data:
                        total_num = int(total_data.replace('(','').replace(')',''))
                        self.second_moudles[name] = {'name':name,'value':value,'total_num':total_num}
                    else:
                        print('在获取第二模块信息时没有获取到 name 或者 value 或者 total_num, 请注意, 再次尝试获取!!!')
                        time.sleep(2)

                print('获取到模块信息为: {}'.format(repr(self.second_moudles)))
                break
            else:
                print('没有获取到当前列表页数据,休息一下5~8min,重新获取!!')

                time.sleep(random.uniform(5, 10))
                if i >= 2:
                    print('列表页连续大于2次没有获取到数据, 等待10~20min重新登录获取数据!!')
                    time.sleep(random.uniform(600, 1200))
                    self.login_again()



    def get_moudles(self,search_info,year):
        # print(self.session.cookies)
        self.years_match = {2023:7,2022:8,2021:9,2020:10,2019:11,2018:12,2017:13,2016:14,2015:15}
        for i in range(5):
            try:
                self.search_info = search_info
                self.cur_year = year
                self.get_moudle_infos()
                if self.session.cookies:
                    return self.session,self.second_moudles
                else:
                    print('获取模块数据时, 发现session中的cookies为空, 重新登录并获取数据!!')
                    self.login_again()
            except Exception as e:
                print('获取moudles信息时出现问题, 休息1~3分钟, 详情为: {}'.format(repr(e)))
                time.sleep(random.uniform(60,180))
                self.login_again()


