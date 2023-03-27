import logging
import random
import re
import time

import requests
from lxml import etree
from ..common.log import FrameLog

from ..common.useragent import useragent_pool
from ..SqlSave.redis_ import RedisCli
from .drugtrial_sql import DtSql


class ChinaDrug():

    auto_id = 0
    def __init__(self):

        self.session = requests.session()
        self.redis_cli = RedisCli()
        self.mongo_cli = DtSql('wfhy','chinadrug')
        self.log = FrameLog('chinadrug_new',logging.DEBUG).get_log()

    def get_session(self):
        '''
        请求首页两次获取session所需的3个cookie
        :return: 包含有3个cookie的session
        '''
        headers = {
            'User-Agent': random.choice(useragent_pool),
            'Referer': 'http://www.chinadrugtrials.org.cn/clinicaltrials.prosearch.dhtml'
        }
        dir_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.prosearch.dhtml'
        r = self.session.get(dir_url, headers=headers)
        first_cookies = dict(r.cookies.items())
        print('first_cookies: ', first_cookies)
        res = self.session.get(dir_url, headers=headers)
        second_cookies = dict(res.cookies.items())
        print('seconde_cookies: ', second_cookies)
        second_cookies.update(first_cookies)
        self.session.cookies.update(second_cookies)
        print('cookies 添加结果为: ', second_cookies, self.session.cookies)
        return self.session

    def get_max_page(self):
        '''
        不输入关键字获取所有的数据, 找出最大页码
        :param max_url:
        :return: 最大页码
        '''
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": random.choice(useragent_pool),
        }
        data = {
            "id": "",
            "ckm_index": "",
            "sort": "desc",
            "sort2": "",
            "rule": "CTR",
            "secondLevel": 0,
            "currentpage": 1,
            "keywords": ""
        }
        list_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml'
        res = self.session.post(list_url, data=data, headers=headers)
        # print(res.text)
        if res.text:
            html = etree.HTML(res.text)
            try:
                maxpage_num = html.xpath('//div[@class="pull-right pageInfo"]/i[2]/text()')[0]
                if maxpage_num:
                    print('最大页码为: ',maxpage_num)
                    return int(maxpage_num)
            except IndexError:
                print('获取最大页码出现了问题, 重新获取session, 获取数据')
                self.get_session()
                time.sleep(2)
                maxpage_num = self.get_max_page()
            return int(maxpage_num)
        else:
            print('获取最大页码错误!!')

    def parser_detail_ids(self, page_data):

        html = etree.HTML(page_data)
        trs = html.xpath('//table[@class="searchTable"]/tr')[1:]
        print(trs)
        detail_ids = []
        for tr in trs:
            detail_id = tr.xpath('./td[2]/a/@id')[0]
            detail_ids.append(detail_id)
        return detail_ids

    def downloader_detail(self, data):

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": random.choice(useragent_pool),
        }
        detail_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlistdetail.dhtml'
        res = self.session.post(detail_url, data=data, headers=headers)
        time.sleep(random.uniform(0,1))
        # print(res)
        if res.status_code == 200 and ('药物名称' in res.text):
            print('详情页请求成功')
            return res.text
        else:
            print('详情页面数据请求状态码异常, 状态码不为200, 或者页面内搜不到searchDetailTable关键字')
            print('这是当前的有问题的html: {}'.format(res.text))
            time.sleep(2)
            self.get_session()
            html = self.downloader_detail(data)
            return html

    def downloader_page_detail(self, detail_ids):

        for detail_id in detail_ids:
            print('这是当前的detail_id: {}'.format(detail_id))

            data = {
                'id': detail_id
            }
            detail_data = self.downloader_detail(data)
            yield detail_data, detail_id

    def get_list_page(self, page_num):

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": random.choice(useragent_pool),
        }
        print('当前是列表页的第 {} 页'.format(page_num))
        data = {
            "id": "",
            "ckm_index": "",
            "sort": "desc",
            "sort2": "",
            "rule": "CTR",
            "secondLevel": 0,
            "currentpage": page_num,
            "keywords": ""
        }
        list_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml'
        res = self.session.post(list_url, data=data, headers=headers)
        if res.status_code == 200 and ('药物名称' in res.text):
            print(res.text)
            return res.text
        else:
            print('列表页请求状态码异常, 请注意!!!! ')
            time.sleep(2)
            print('列表页数据请求出现问题, 准备重新获取数据')
            print('有问题的列表页html为: {}'.format(res.text))
            self.get_session()
            page_html = self.get_list_page(page_num)
            return page_html

    def parse_detail_html(self, detail_html):
        '''
        解析详情页目标数据, 获取 登记号、药物名称、申请人信息： 姓名，联系人手机号，email, 主要研究者信息:
        姓名 职称 电话 email 单位名称  济南市中心医院
        :param detail_html:
        :return:
        '''
        html = etree.HTML(detail_html)
        # 获取基本信息
        base_tds = html.xpath('//div[@id="collapseOne"]//table[1]//td')
        print('这是base_tds: ',base_tds)
        register_num = base_tds[0].xpath('./text()')[0]
        register_data = base_tds[2].xpath('./text()')
        if register_data:
            register_people = register_data[0]
        else:
            register_people = ''
        register_date_data = base_tds[3].xpath('./text()')
        if register_date_data:
            register_date = register_date_data[0].strip()
        else:
            register_date = ''
        # 获取申请人信息
        trs = html.xpath('//div[@id="collapseTwo"]//table[2]/tr')[1:]
        print('这是trs: ', trs)
        tds = []
        items = []
        for tr in trs:
            # print(tr)
            tds.extend(tr.xpath('./td'))
        name_data = tds[0].xpath('./text()')
        zuoji_data = tds[1].xpath('./text()')
        phone_data = tds[2].xpath('./text()')
        email_data = tds[3].xpath('./text()')
        if name_data:
            name = name_data[0]
        else:
            name = ''
        if zuoji_data:
            zuoji_number = zuoji_data[0]
        else:
            zuoji_number = ''
        print('这是座机数据: {}'.format(zuoji_number))
        if phone_data:
            phone = phone_data[0]
        else:
            phone = ''
        if email_data:
            email = email_data[0]
        else:
            email = ''
        if (phone_data and re.match('(\d+){11}', phone_data[0])) or (zuoji_data and re.match('(\d+){11}', zuoji_data[0])):
            items.append([name, phone, email, zuoji_number,register_num, register_people, register_date])
            # print('这是姓名: {},这是电话: {}, 这是邮箱: {}'.format(name,phone_data[0],email))
        else:
            print('当前的手机号不是标准手机号: ', phone_data)
        # 获取主要负责人信息
        try:
            tds = html.xpath('//table[@class="searchDetailTable marginBtm10"]//td')
            leader_name_data = tds[0].xpath('./text()')
            if leader_name_data:
                leader_name = leader_name_data[0]
            else:
                leader_name = ''
            zuoji_number = ''
            # position = tds[2].xpath('./text()')[0]
            leader_phone_data = tds[3].xpath('./text()')
            leader_email_data = tds[4].xpath('./text()')
            if leader_email_data:
                leader_email = leader_email_data[0]
            else:
                leader_email = ''
            if leader_phone_data and re.match('(\d+){11}', leader_phone_data[0]):
                items.append([leader_name, leader_phone_data[0], leader_email, zuoji_number, register_num, register_people, register_date])
            print('这是items: ', items)
        except IndexError as e:
            self.log.info(repr(e))
            self.log.info('当前页面数据为: {}'.format(detail_html))
            # self.log.de
        return items


    def duplicate_save(self, items,detail_id,page_num):
        for item in items:
            name = item[0]
            phone = item[1]
            email = item[2]
            status = self.redis_cli.set_item('chinadrug_new', phone)
            if status == 1:
                ChinaDrug.auto_id += 1
                dic = {}
                dic['name'] = name
                dic['phone'] = phone
                dic['email'] = email
                dic['zuoji'] = item[3]
                dic['register_num'] = item[4]
                dic['register_people'] = item[5]
                dic['register_date'] = item[6]
                dic['detail_id'] = detail_id
                dic['page_num'] = page_num
                self.mongo_cli.insert(dic)

            elif status == 0:
                print('检测到已经抓取过')
            else:
                print('入库失败!!')

    # def get_auto_id(self):
    #
    #     item = self.mongo_cli.find_max_autoid()
    #     print('mongo数据库中最大id数据为: ',item)
    #     if item:
    #         ChinaDrug.auto_id = item['max_auto_id']

    def get_maxcard(self):

        item = self.mongo_cli.find_max_card()
        if item:
            self.max_register_num = item['max_register_num']
            print('这是数据库中最大的注册号: {}'.format(self.max_register_num))
        else:
            print('从数据库中未能获取到最大注册号')
            self.max_register_num = ''

    def get_increase_page(self):

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": random.choice(useragent_pool),
        }
        i = 1
        while 1:
            data = {
                "id": "",
                "ckm_index": "",
                "sort": "desc",
                "sort2": "",
                "rule": "CTR",
                "secondLevel": 0,
                "currentpage": i,
                "keywords": ""
            }
            list_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlist.dhtml'
            res = self.session.post(list_url, data=data, headers=headers)

            if res.text:
                html = etree.HTML(res.text)
                try:
                    first_register_card = html.xpath('//tr[@class="Tab_title"][1]/following-sibling::tr[1]/td[2]/a/text()')[0].strip()
                    if first_register_card and (first_register_card > self.max_register_num):
                        print('当前是列表第 {} 页, 可抓取'.format(i))
                        i += 1
                    else:
                        return i
                except IndexError:
                    print('获取最大页码出现了问题, 重新获取session, 获取数据')
                    self.get_session()
                    time.sleep(2)
            else:
                print('获取最大页码错误!!')

    def run(self):

        # self.get_auto_id()
        self.get_session()
        self.get_maxcard()
        if self.max_register_num:
            spider_page_num = self.get_increase_page()
            print('当前更新列表页数量为: {}'.format(spider_page_num))
            print('开始抓取更新页面...')
            time.sleep(2)
            for i in range(1, spider_page_num):
                res_data = self.get_list_page(page_num=i)
                # print('这是列表页返回数据: ',res_data)
                # for detail_id in self.parser_detail_ids(res_data):
                detail_ids = self.parser_detail_ids(res_data)
                detail_htmls = self.downloader_page_detail(detail_ids)
                for detail_html_data in detail_htmls:
                    detail_html = detail_html_data[0]
                    detail_id = detail_html_data[1]
                    #     # print('这是detail_html: ', detail_html)
                    items = self.parse_detail_html(detail_html)
                    print(items)
                    self.duplicate_save(items,detail_id,i)
        else:
            print('获取最新更新页数据为空! 请查看代码!!')

# 需要设置一个字段, 当前字段首先从数据库中获取最大值, 然后在持续做新的爬取
# 增量抓取的思路为  识别出当前页面的最大登记号与数据库中最大register_num进行比对, 大于register_num证明当前页面有数据更新,那么更新页码数字spider_page_num增加1, 直至小于register_num ,此时,查看第一页更新的数据