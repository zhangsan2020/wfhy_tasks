import logging
import random
import re
import time
from datetime import datetime

import requests
from lxml import etree
from ..common.log import FrameLog
from ..common.useragent import useragent_pool
from ..SqlSave.redis_ import RedisCli
from .drugtrial_sql import DtSql


class ChinaDrug():

    def __init__(self):

        self.session = requests.session()
        self.redis_cli = RedisCli()
        self.mongo_cli = DtSql('wfhy_update', 'chinadrug_all')
        self.mongo_cli_commit = DtSql('wfhy_commit', 'chinadrug_commit')
        self.log = FrameLog('chinadrug_new', logging.DEBUG).get_log()

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
            "currentpage": 3,
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
                    print('最大页码为: ', maxpage_num)
                    return int(maxpage_num)
            except IndexError:
                print('获取最大页码出现了问题, 重新获取session, 获取数据')
                self.log.debug(repr(IndexError))
                self.get_session()
                time.sleep(2)
                maxpage_num = self.get_max_page()
            return int(maxpage_num)
        else:
            print('获取最大页码错误!!')

    def parser_detail_ids(self, page_data):

        html = etree.HTML(page_data)
        detail_ids = []
        if html.xpath('//table[@class="searchTable"]/tr')[1:]:
            trs = html.xpath('//table[@class="searchTable"]/tr')[1:]
            # print('这是当前页面列表页获取到的trs: ',trs)
            if trs:
                for tr in trs:
                    detail_id = tr.xpath('./td[2]/a/@id')[0]
                    detail_ids.append(detail_id)
            else:
                print('列表页trs没有获取到, 请查看源代码: {}'.format(page_data))
        elif html.xpath('//div[@class="paddingSide15 bgGrey"]/table/tr[1]/td[1]/a/@id'):
            detail_ids = html.xpath('//div[@class="paddingSide15 bgGrey"]/table/tr[1]/td[1]/a/@id')

        return detail_ids

    def downloader_detail(self, data):

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": random.choice(useragent_pool),
        }
        detail_url = 'http://www.chinadrugtrials.org.cn/clinicaltrials.searchlistdetail.dhtml'
        res = self.session.post(detail_url, data=data, headers=headers)
        time.sleep(random.uniform(0, 1))
        # print(res)
        if res.status_code == 200 and ('药物名称' in res.text):
            # print('详情页请求成功')
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
        # print('这是base_tds: ',base_tds)
        register_num = base_tds[0].xpath('./text()')[0].strip()
        register_data = base_tds[2].xpath('./text()')
        if register_data:
            register_people = register_data[0].strip()
        else:
            register_people = ''
        register_date_data = base_tds[3].xpath('./text()')
        if register_date_data:
            register_date = register_date_data[0].strip()
        else:
            register_date = ''
        # 题目和背景信息
        backgroud_trs = html.xpath('//div[@id="collapseTwo"]//table[@class="searchDetailTable"][1]/tr')
        drug_name_info = backgroud_trs[2].xpath('./td[1]/text()')
        if drug_name_info:
            drug_name = drug_name_info[0].replace('\xa0', '').replace('\t', '').replace('\r\n', '').strip()
        else:
            drug_name = ''
        # print(drug_name * 20)
        drug_type_info = backgroud_trs[3].xpath('./td[1]/text()')
        if drug_type_info:
            drug_type = drug_type_info[0].strip()
        else:
            drug_type = ''
        drug_apply_info = backgroud_trs[5].xpath('./td[1]/text()')
        if drug_apply_info:
            drug_apply = drug_apply_info[0].strip()
        else:
            drug_apply = ''
        # print(drug_apply)

        drug_title_info = backgroud_trs[6].xpath('./td[1]/text()')
        if drug_title_info:
            drug_title = drug_title_info[0].strip()
        else:
            drug_title = ''
        # print(drug_title)
        # exit()
        # 获取申请人信息
        trs = html.xpath('//div[@id="collapseTwo"]//table[2]/tr')[1:]
        # print('这是trs: ', trs)
        tds = []
        items = []
        for tr in trs:
            # print(tr)
            tds.extend(tr.xpath('./td'))
        name_data = tds[0].xpath('./text()')
        zuoji_data = tds[1].xpath('./text()')
        phone_data = tds[2].xpath('./text()')
        email_data = tds[3].xpath('./text()')
        reg_company_info = html.xpath('//input[@class="form-control"]/@value')
        if reg_company_info:
            reg_company = reg_company_info[0].strip()
        else:
            reg_company = ''
        if name_data:
            name = name_data[0].strip()
        else:
            name = ''
        if zuoji_data:
            zuoji_number = zuoji_data[0].strip()
        else:
            zuoji_number = ''
        if phone_data:
            phone = phone_data[0].strip()
        else:
            phone = ''
        if email_data:
            email = email_data[0].strip()
        else:
            email = ''
        if (phone_data and re.match('1(\d+){10}', phone_data[0])) or (
                zuoji_data and re.match('1(\d+){10}', zuoji_data[0])):
            items.append(
                [name, phone, email, zuoji_number, register_num, register_people, register_date, reg_company, drug_name,
                 drug_apply, drug_title, drug_type])
            # print('这是姓名: {},这是电话: {}, 这是邮箱: {}'.format(name,phone_data[0],email))
        else:
            print('当前的手机号不是标准手机号: ', phone_data)
        # 获取主要负责人信息
        try:
            tds = html.xpath('//table[@class="searchDetailTable marginBtm10"]//td')
            leader_name_data = tds[0].xpath('./text()')
            if leader_name_data:
                leader_name = leader_name_data[0].strip()
            else:
                leader_name = ''
            zuoji_number = ''
            # position = tds[2].xpath('./text()')[0]
            leader_phone_data = tds[3].xpath('./text()')
            leader_email_data = tds[4].xpath('./text()')
            leader_company_data = tds[7].xpath('./text()')
            if leader_email_data:
                leader_email = leader_email_data[0].strip()
            else:
                leader_email = ''
            if leader_company_data:
                leader_company = leader_company_data[0].strip()
            else:
                leader_company = ''
            if leader_phone_data and re.match('1(\d+){10}', leader_phone_data[0]):
                items.append([leader_name, leader_phone_data[0].strip(), leader_email, zuoji_number, register_num,
                              register_people, register_date, leader_company, drug_name, drug_apply, drug_title,
                              drug_type])
            print('这是items: ', items)
            # exit()
        except IndexError as e:
            self.log.info(repr(e))
            self.log.info('当前页面数据为: {}'.format(detail_html))
            # self.log.de
        return items

    def duplicate_save(self, items, detail_id, page_num):
        for item in items:
            dic = {}
            dic['name'] = item[0]
            dic['phone'] = item[1]
            dic['email'] = item[2]
            dic['landline'] = item[3]
            dic['register_num'] = item[4]
            dic['register_people'] = item[5]
            dic['register_date'] = item[6]
            dic['company'] = item[7]
            dic['drug_name'] = item[8]
            dic['drug_apply'] = item[9]
            dic['title'] = item[10]
            dic['drug_type'] = item[11]
            dic['detail_id'] = detail_id
            dic['page_num'] = page_num
            spider_date = datetime.now().strftime('%Y%m%d%H%M')
            dic['spider_date'] = spider_date
            self.mongo_cli.insert(dic)
            # 判断手机号与座机号情况, 哪个存在数据就以哪个作为去重依据存入到redis数据库中
            if item[1]:
                status = self.redis_cli.set_item('chinadrug', item[1])
            elif item[3]:
                status = self.redis_cli.set_item('chinadrug', item[3])
            else:
                status = 0
            if status == 1:
                dic.clear()
                dic['name'] = item[0]
                dic['phone'] = item[1]
                dic['email'] = item[2]
                dic['landline'] = item[3]
                dic['register_num'] = item[4]
                dic['spider_date'] = spider_date
                dic['commit_status'] = '未提交'
                dic['commit_date'] = ''
                self.mongo_cli_commit.insert(dic)
            elif status == 0:
                print('检测到之前已经抓取过,不再重复放入去重库与提交库中')
            else:
                print('入库失败!!')

    def get_sql_maxpage(self):

        sql_max_page = self.mongo_cli.find_max_sqlpage()
        print('mongo数据库中页码数为: ',sql_max_page)
        return sql_max_page

    def run(self):
        self.log.info('开始抓取 chinadrug...')
        self.get_session()
        # sql_max_page = self.get_sql_maxpage()
        web_max_page = self.get_max_page()
        update_page_num = web_max_page
        # self.log.info('检测到最大页码是: {}'.format(max_page_num))
        # print('即将抓取的最大页码是: {}'.format(max_page_num))
        # update_page_num = web_max_page - sql_max_page + 1
        print('网站页面最大页码数为: {}, 更新页码数为: {}'.format(web_max_page,update_page_num))
        time.sleep(3)
        if update_page_num > 0:
            print('chinadrug 网站页面有更新, 最新最大页码数为: {}'.format(update_page_num))
            for i in range(update_page_num,0,-1):
                print('当前是第 {} 页'.format(i))
                res_data = self.get_list_page(page_num=i)
                if res_data:
                    # print('这是列表页返回数据: ',res_data)
                    # for detail_id in self.parser_detail_ids(res_data):
                    detail_ids = self.parser_detail_ids(res_data)
                    if detail_ids:
                        print('这是detail_ids: ', detail_ids)
                        detail_htmls = self.downloader_page_detail(detail_ids)
                        for detail_html_data in detail_htmls:
                            detail_html = detail_html_data[0]
                            detail_id = detail_html_data[1]
                            items = self.parse_detail_html(detail_html)
                            self.duplicate_save(items, detail_id, i)
                    else:
                        print('没有获取到列表页详情id,退出')
                        self.log.error('第 {} 页数据详情id没有获取到'.format(i))
                        # exit()
                else:
                    print('第 {} 页列表页数据没有获取到, 请注意查看!!'.format(i))

        self.log.info('抓取结束!!!')
