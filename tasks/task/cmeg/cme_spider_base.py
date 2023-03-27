import random
import re
import time
from datetime import datetime

import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from .cme_login import CmeLogin
from .cme_mongo import CmeMongo
from ..SqlSave.redis_ import RedisCli


class CmeSpiderBase():

    def __init__(self):

        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.cmelogin = CmeLogin()
        self.page_size = 150
        self.cme_config = {'page_size': 150, 'max_year': 2023, 'min_year': 2020}
        self.cme_mongo_all = CmeMongo('wfhy_update', 'cme_all')
        self.cme_mongo_commit = CmeMongo('wfhy_commit', 'cme_commit')
        self.cme_redis = RedisCli()
        self.item = {}

    def get_page_num(self, page=1):

        headers = {
            "Host": "cmegsb.cma.org.cn",
            "Connection": "keep-alive",
            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "iframe",
            "Referer": "https://cmegsb.cma.org.cn/national_project/projectGongbuList.do",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cookie": "JSESSIONID=CB73F41CF4F6BF45493498CFAE018AB1; cmegsbsid=37cfa8ea-521a-4f05-bcbc-e9dcbe443036"
        }
        for i in range(10):
            self.session.cookies.clear()
            self.session, code_res = self.cmelogin.login(self.session)
            # https://cmegsb.cma.org.cn/national_project/projectGongbuList.do?parentSubjectId=&xmanager=&scode=&year=2023&sdanwei=&gongbuCode=&gongbu=3&beian=&orderBy=danwei&pageSize=150&pici=&type=3&subjectId=&checkCode=2&d-1342871-p=2&name=
            # first_list = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do?parentSubjectId=&xmanager=&scode=&year={}&gongbuCode=&gongbu=3&sdanwei=&beian=&orderBy=subject&pageSize={}&pici=&type=&subjectId=&checkCode={}&d-1342871-p={}&name='.format(
            #     self.cur_year, self.cme_config['page_size'], code_res, page)
            first_list = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do?parentSubjectId=&xmanager=&scode=&year={}&sdanwei=&gongbuCode=&gongbu=3&beian=&orderBy=danwei&pageSize={}&pici=&type=3&subjectId=&checkCode={}&d-1342871-p={}&name='.format(
                self.cur_year, self.cme_config['page_size'], code_res, page)
            res = self.session.get(first_list, headers=headers)
            if res.status_code == 200:
                # print(res.text)
                html = etree.HTML(res.text)
                page_data = html.xpath('//span[@class="pagebanner"]/div/text()')
                if page_data:
                    print('页面内获取页码数据为: ', page_data)
                    # [' 找到13,641条数据, 当前显示第1页/共91页. ']
                    # total = re.findall('找到(\d+),(\d+)条数据',page_data)
                    new_max_page = re.findall('显示第1页/共(\d+)页', page_data[0])
                    if new_max_page:
                        max_page_web = int(new_max_page[0]) + 1
                        mongo_page = int(self.get_mongo_max_pagenum())
                        if mongo_page == 0:
                            print('当前年还未抓取过数据! 从第一页开始抓取!!')
                            min_page = 1
                            max_page = max_page_web
                        elif mongo_page >= max_page_web:
                            print('当前年已经抓取完成, 不再继续抓取')
                            return 'have_spider_over'
                        else:
                            max_page = max_page_web
                            min_page = mongo_page
                        return min_page, max_page
                    else:
                        print('页面中未获取到最大页码!! 重新请求获取')
                    print(new_max_page)
                else:
                    print('列表页面中没有拿到总数与最大页面数, 重新请求获取')
            else:
                print('获取最大页面数连接状态码异常, 重新请求获取')
            time.sleep(random.uniform(2, 5))

    def get_mongo_max_pagenum(self):

        res = self.cme_mongo_all.find_base_max_page(self.cur_year)
        return res

    def get_page_list(self):

        headers = {
            "Host": "cmegsb.cma.org.cn",
            "Connection": "keep-alive",
            "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "iframe",
            "Referer": "https://cmegsb.cma.org.cn/national_project/projectGongbuList.do",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            # "Cookie": "JSESSIONID=CB73F41CF4F6BF45493498CFAE018AB1; cmegsbsid=37cfa8ea-521a-4f05-bcbc-e9dcbe443036"
        }
        for i in range(10):
            self.session.cookies.clear()
            self.session, code_res = self.cmelogin.login(self.session)
            print('进入列表页,当前是 {} 年 第 {} 页数据'.format(self.cur_year, self.cur_page))
            # first_list = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do?parentSubjectId=&xmanager=&scode=&year={}&gongbuCode=&gongbu=3&sdanwei=&beian=&orderBy=subject&pageSize={}&pici=&type=&subjectId=&checkCode={}&d-1342871-p={}&name='.format(self.cur_year, self.cme_config['page_size'], code_res, self.cur_page)
            first_list = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do?parentSubjectId=&xmanager=&scode=&year={}&sdanwei=&gongbuCode=&gongbu=3&beian=&orderBy=danwei&pageSize={}&pici=&type=3&subjectId=&checkCode={}&d-1342871-p={}&name='.format(
                self.cur_year, self.cme_config['page_size'], code_res, self.cur_page)
            res = self.session.get(first_list, headers=headers)
            time.sleep(random.uniform(1, 2))
            if res.status_code == 200:
                html = etree.HTML(res.text)
                trs = html.xpath('//table[@id="project"]/tbody/tr')
                print('这是trs: ', trs)
                if trs:
                    for tr in trs:
                        self.item.clear()
                        tds = tr.xpath('.//td')
                        self.item['project_num'] = tds[0].xpath('./text()')[0].strip()
                        self.item['project_name'] = tds[4].xpath('./text()')[0].strip()
                        self.item['unit'] = tds[1].xpath('./text()')[0].strip()
                        self.item['name'] = tds[5].xpath('./text()')[0].strip()
                        self.item['phone'] = tds[3].xpath('./text()')
                        second_phone = tds[6].xpath('./text()')
                        self.item['phone'].extend(second_phone)
                        if tds[9].xpath('./text()'):
                            self.item['student_num'] = tds[11].xpath('./text()')[0].strip()
                        else:
                            self.item['student_num'] = 0
                        self.item['cur_page'] = self.cur_page
                        self.item['year'] = self.cur_year
                        self.save()
                    break
                else:
                    print('第 {} 次列表页数据获取出现问题,没有tr数据,重新获取'.format(i))
                    print('列表页获取有问题, 没有获取到tr数据, 休息一下, 重新发起请求获取列表页数据')
                    time.sleep(random.uniform(5,10))
            else:
                print('第 {} 次列表页数据获取出现问题, 休息一下, 状态码出现异常重新获取'.format(i))
                time.sleep(random.uniform(5, 10))


    def save(self):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        self.item['spider_date'] = spider_date
        self.item['origin_type'] = '基地项目'
        self.cme_mongo_all.insert(self.item)
        # 13981880412
        print('当前item为: ',self.item)
        print('这是手机号: ',self.item['phone'])
        # time.sleep(2)
        if self.item['phone']:
            for phone in self.item['phone']:
                if re.findall('(1[35678]\d{9})', phone):
                    status = self.cme_redis.set_item('cme_phones', phone)
                    if status == 1:
                        self.item['phone'] = phone
                        print('发现新数据, 且存在手机号, 可以插入到commit表中')
                        self.item['commit_status'] = '未提交'
                        self.cme_mongo_commit.insert(self.item)
                    else:
                        print('该手机号之前已经抓取过, 不再放入commit表中')
                else:
                    print('检测到新数据, 但联系方式是座机, 不加入到commit表中')
        self.item.clear()

    def run(self):

        for year in range(self.cme_config['max_year'], self.cme_config['min_year'], -1):
            self.cur_year = year
            max_page_data = self.get_page_num()
            print('当前是 {} 年, 最大页码信息为: '.format(self.cur_year), max_page_data)
            if max_page_data == 'have_spider_over':
                print('当前年已经抓取完成, 直接进入下一年进行抓取!!')
            else:
                min_page, max_page = max_page_data
                self.cur_page = min_page
                print('当前页码为: {}, 最大页码为: {}'.format(self.cur_page, max_page))
                while self.cur_page < max_page:
                    self.get_page_list()
                    self.cur_page += 1

# if __name__ == '__main__':
#
#     cme_spider = CmeSpider()
#     cme_spider.get_page_list()
