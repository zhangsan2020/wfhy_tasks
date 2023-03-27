import os
import random
import re
import time

from lxml import etree
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from ..SqlSave.redis_ import RedisCli
from ..SqlSave.mongo_store import MongoStore
from ..common.useragent import useragent_pool


# url = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do'
#
# res = requests.post()
#
class ChiCtr():

    def __init__(self):

        # self.wb = Workbook()
        # self.sheet = self.wb.active
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.redis_cli = RedisCli()
        self.mongo_cli = MongoStore('wfhy_update', 'chictr_all')
        self.mongo_cli_commit = MongoStore('wfhy_commit', 'chictr_commit')

    def downlaoder(self, url):
        ua = random.choice(useragent_pool)
        retry_num = 1
        # time.sleep(random.uniform(0,0.5))
        headers = {
            "User-Agent": ua
        }
        try:
            res = self.session.get(url, headers=headers)
            if res.status_code == 200:
                return res.text
            else:
                if retry_num <= 3:
                    print('下载状态异常!! 等待2秒钟重新下载该链接地址url: {}'.format(url))
                    time.sleep(2)
                    retry_num += 1
                    return self.downlaoder(url)
        except Exception as e:
            print(str(e))

    def parser_list(self, data):

        html = etree.HTML(data)
        trs = html.xpath('//table[@class="table_list"]/tbody/tr')[1:]
        detail_urls = []
        for tr in trs:
            tds = tr.xpath('./td')
            card_id = tds[1].text.strip()
            title = tds[2].text.strip()
            detail_url = 'http://www.chictr.org.cn/' + tds[2].xpath('./p/a/@href')[0]
            type = tds[3].text.strip()
            date = tds[4].text.strip()
            print(card_id, title, detail_url, type, date)
            detail_urls.append(detail_url)
        return detail_urls

    def parse_detail(self, html):

        page_items = []
        page_html = etree.HTML(html)
        target_html = page_html.xpath('//div[@class="ProjetInfo_ms"]')[1]
        trs_1 = target_html.xpath('./table/tbody/tr')
        if trs_1[2].xpath('./td[2]/text()') or trs_1[2].xpath('./td[4]/text()'):
            sq_name = trs_1[0].xpath('./td[2]/p/text()')[0].strip()
            yj_name = trs_1[0].xpath('./td[4]/p/text()')[0].strip()
            sq_phone = trs_1[2].xpath('./td[2]/text()')[0].strip()
            yj_phone = trs_1[2].xpath('./td[4]/text()')[0].strip()
            sq_email = trs_1[4].xpath('./td[2]/text()')[0].strip()
            yj_email = trs_1[4].xpath('./td[4]/text()')[0].strip()
            sq_addr = trs_1[6].xpath('./td[2]/p/text()')[0].strip()
            yj_addr = trs_1[6].xpath('./td[4]/p/text()')[0].strip()
            sq_unit = trs_1[9].xpath('./td[2]/p/text()')[0].strip()
            # print(sq_addr,yj_addr,sq_unit)
            # print(sq_name,yj_name,sq_phone,yj_phone)
            # 需补充字段信息, 用于后期的数据分析
            target_html_0 = page_html.xpath('//div[@class="ProjetInfo_ms"]')[0]
            trs_0 = target_html_0.xpath('./table/tbody/tr')
            reg_number = trs_0[0].xpath('./td[2]/text()')[0].strip()
            reg_date = trs_0[2].xpath('./td[2]/text()')[0].strip()
            update_date = trs_0[1].xpath('./td[2]/text()')[0].strip()
            title = trs_0[9].xpath('./td[2]/p/text()')[0].strip()
            # print(reg_number, reg_date, update_date, title)
            # 补充研究类型字段
            target_html_3 = page_html.xpath('//div[@class="ProjetInfo_ms"]')[3]
            trs_3 = target_html_3.xpath('./table/tbody/tr')
            study_type = trs_3[11].xpath('./td[2]/p/text()')[0].strip()
            if sq_phone and (re.findall('1(\d+){10}', sq_phone)):
                page_items.append(
                    [reg_number, reg_date, update_date, title, study_type, sq_name, sq_phone, sq_email, sq_addr,
                     sq_unit])
            if yj_phone and (re.findall('1(\d+){10}', yj_phone)):
                page_items.append(
                    [reg_number, reg_date, update_date, title, study_type, yj_name, yj_phone, yj_email, yj_addr])
            return page_items

    def duplicate_(self, page_target_info, detail_url):
        print("进入了去重函数!")
        for info in page_target_info:
            mongo_dic = {}
            mongo_dic['reg_number'] = info[0]
            mongo_dic['reg_date'] = info[1]
            mongo_dic['update_date'] = info[2]
            mongo_dic['title'] = info[3]
            mongo_dic['study_type'] = info[4]
            mongo_dic['name'] = info[5]
            mongo_dic['phone'] = info[6]
            mongo_dic['email'] = info[7]
            mongo_dic['sq_addr'] = info[8]
            if len(info) == 10:
                mongo_dic['sq_unit'] = info[9]
            spider_date = datetime.now().strftime('%Y%m%d%H%M')
            mongo_dic['spider_date'] = spider_date
            mongo_dic['detail_url'] = detail_url
            url_id = int(re.findall('=(\d+)', detail_url)[0])
            mongo_dic['url_id'] = url_id
            self.mongo_cli.insert(mongo_dic)
            # 存入提交mongo数据库表
            status = self.redis_cli.set_item('chictr', info[6])
            if status == 1:
                mongo_commit = {}
                mongo_commit['name'] = info[5]
                mongo_commit['phone'] = info[6]
                mongo_commit['email'] = info[7]
                mongo_commit['spider_date'] = spider_date
                mongo_commit['detail_url'] = detail_url
                mongo_commit['url_id'] = url_id
                mongo_commit['commit_status'] = '未提交'
                mongo_commit['commit_date'] = ''
                self.mongo_cli_commit.insert(mongo_commit)
                print('发现新数据, 已加入到 chictr_commit 表中!!!')
            elif status == 0:
                print('检测到之间已经抓去过, 不在重复放入 chictr_commit 表中!!!')
            else:
                print('插入数据库出现异常!!!')

    def mongo_maxuid(self):
        # print(dir(self.mongo_cli))
        datas = self.mongo_cli_commit.find_(sort_field='url_id', sort_type=-1, limit_num=1)
        print(datas)
        if datas:
            for data in datas:
                max_uid = data['url_id']
                print('mongo中最大ID为: ', max_uid)
                return max_uid
        else:
            print('chictr表中没有查到当前最大的url_id, 无法做出数据更新计算!!')

    def page_maxuid(self):
        # 获取前3页的urlid,找出最大值,然后与数据库中最大url_id进行比较, 如果大于数据库, 说明最近有更新, 可进行抓取最大值与数据库中间id的页面数据
        ua = random.choice(useragent_pool)
        hrefs_all = []

        headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                # "Cookie": "bhsstemplateid_1_0_0=25; onlineusercount=1; acw_tc=707c9fc516775510067634808e73fcdec58cd976129149e0c44eb4808b5d3b",
                "Host": "www.chictr.org.cn",
                "Referer": "https://www.chictr.org.cn/searchproj.aspx",
                "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
            }
        for page in range(1, 6):
            res = self.session.get(
                'https://www.chictr.org.cn/searchproj.aspx?title=&officialname=&subjectid=&secondaryid=&applier=&studyleader=&ethicalcommitteesanction=&sponsor=&studyailment=&studyailmentcode=&studytype=0&studystage=0&studydesign=0&minstudyexecutetime=&maxstudyexecutetime=&recruitmentstatus=0&gender=0&agreetosign=&secsponsor=&regno=&regstatus=0&country=&province=&city=&institution=&institutionlevel=&measure=&intercode=&sourceofspends=&createyear=0&isuploadrf=&whetherpublic=&btngo=btn&verifycode=&page={}'.format(
                    page), headers=headers)
            res.encoding = 'utf-8'
            if res.status_code == 200:
                html = etree.HTML(res.text)
                # reg_num = html.xpath('//table[@class="table_list"][1]/tbody/tr[2]/td[2]/text()')[0].strip()
                hrefs = html.xpath('//table[@class="table_list"][1]/tbody//p/a/@href')
                hrefs_all.extend(hrefs)
            else:
                print('请求出现问题')
                print(res.text)
        print(hrefs_all)
        if hrefs_all:
            max_uid = int(re.findall('proj=(\d+)', max(hrefs_all))[0])
            print('页面最大ID为: ', max_uid)
            return max_uid
        else:
            print('获取最大ID环节, 页面hrefs没有获取到!!!')

    def num_to_num(self):

        sql_maxuid = self.mongo_maxuid()
        page_maxuid = self.page_maxuid()
        if page_maxuid > sql_maxuid:
            print('检测到chictr网站当前有数据更新, 起始ID为 {},结束ID为 {}'.format(page_maxuid, sql_maxuid))
            return page_maxuid, sql_maxuid
        else:
            print('chictr网站未检测到数据更新')

    def run(self):

        items = self.num_to_num()
        if items:
            max_num, min_num = self.num_to_num()
            # 66329
            max_num += 1
            for i in range(min_num, max_num):
                pass
                detail_url = "http://www.chictr.org.cn/showproj.aspx?proj={}".format(i)
                print('当前链接地址是 {} '.format(detail_url))
                detail_html = self.downlaoder(detail_url)
                if detail_html and (not '非常抱歉!您查' in detail_html):
                    page_target_info = self.parse_detail(detail_html)
                    # print(page_target_info)
                    if page_target_info:
                        print('这是page_target_info', page_target_info)
                        self.duplicate_(page_target_info, detail_url)
                    else:
                        print('当前详情页面获取不到电话信息')


if __name__ == '__main__':
    cc = ChiCtr()
    cc.run()
