import os
import random
import re
import time
from PIL import Image
import pytesseract
from os import path
from ..common.chaojiying import Chaojiying_Client
from lxml import etree
from datetime import datetime
import csv
import requests
from openpyxl import Workbook
from ..SqlSave.redis_ import RedisCli
from ..SqlSave.mongo_store import MongoStore
from ..common.useragent import useragent_pool
import logging

# url = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do'
#
# res = requests.post()
#
class ChiCtr():

    def __init__(self):

        self.log_do()
        self.wb = Workbook()
        self.sheet = self.wb.active
        self.redis_cli = RedisCli()
        self.mongo_cli = MongoStore('wfhy','chictr')
        self.cur_dir = os.path.dirname(os.path.realpath(__file__))
        # self.imgcode_path = self.cur_dir + '\imgs\chictr_img_code.jpeg'
        # print(os.path.dirname(os.path.realpath(__file__)))
        # print(self.imgcode_path)
        date = datetime.now().strftime('%Y%m%d%H%m')
        self.filename = self.cur_dir + '\chictrdata\chictrdata数据表_{}.xlsx'.format(date)
        self.sheet.title = 'cmeg网站2022年发布信息'
        self.sheet.append(['姓名', '手机号', '邮箱'])

    def downlaoder(self,url):
        ua = random.choice(useragent_pool)
        time.sleep(random.uniform(3,20))
        headers = {
            "User-Agent":ua
        }
        res = requests.get(url,headers=headers)
        if res.status_code == 200:
            # print(res.text)
            return res.text
        else:
            print('下载状态异常!!')

    def parser_list(self,data):

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
            print(card_id,title,detail_url,type,date)
            detail_urls.append(detail_url)
        return detail_urls
    def log_do(self):

        # 1、创建一个logger
        logger = logging.getLogger('mylogger')
        logger.setLevel(logging.DEBUG)

        # 2、创建一个handler，用于写入日志文件
        fh = logging.FileHandler('chictr.log')
        fh.setLevel(logging.DEBUG)
        # 3、定义handler的输出格式（formatter）
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # 4、给handler添加formatter
        fh.setFormatter(formatter)
        # 5、给logger添加handler
        logger.addHandler(fh)

    def parse_detail(self,html):

        page_items = []
        page_html = etree.HTML(html)
        target_html = page_html.xpath('//div[@class="ProjetInfo_ms"]')[1]
        trs = target_html.xpath('./table/tbody/tr')
        # print(trs)
        sq_name = trs[0].xpath('./td[2]/p/text()')[0].strip()
        yj_name = trs[0].xpath('./td[4]/p/text()')[0].strip()
        sq_phone = trs[2].xpath('./td[2]/text()')[0].strip()
        yj_phone = trs[2].xpath('./td[4]/text()')[0].strip()
        sq_email = trs[4].xpath('./td[2]/text()')[0].strip()
        yj_email = trs[4].xpath('./td[4]/text()')[0].strip()
        # print(sq_name,yj_name,sq_phone,yj_phone)
        page_items.append([sq_name,sq_phone,sq_email])
        page_items.append([yj_name,yj_phone,yj_email])
        print(page_items)
        return page_items

    def duplicate_(self,page_target_info,detail_url):

        for info in page_target_info:
            md5_str = info[0] + info[1]
            status = self.redis_cli.set_item('chictr',md5_str)
            if status == 1:
                mongo_dic = {}
                mongo_dic['name'] = info[0]
                mongo_dic['phone'] = info[1]
                mongo_dic['email'] = info[2]
                mongo_dic['detail_url'] = detail_url
                print('新数据, 以加入到mongodb中!!!')
                self.mongo_cli.insert(mongo_dic)
                yield info
            elif status == 0:
                print('之前已经抓取过,且放入到redis与mongo中, 舍去')
            else:
                print('存入数据去重数据库异常')



    def save_data(self,items):
        if items:
            # date = datetime.now().strftime('%Y%m%d%H%m')
            # filename = self.cur_dir + '\cmegdata\cmeg数据表_{}.xlsx'.format(date)
            # self.sheet.title = 'cmeg网站2022年发布信息'
            # self.sheet.append(['姓名','手机号'])
            for item in items:
                self.sheet.append([item[0], item[1], item[2]])

            # writer.writerow([item['title'], item['abstract'], item['nickname']])
            # with open('cmegsb_2022.csv','w',encoding='utf-8',newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerow(['姓名', '电话'])
            #     writer.writerows(items)
        # else:
        #     print('今日网站无更新数据!')
    def close_driver(self):

        self.wb.save(self.filename)
        self.wb.close()
        # self.redis_cli

    def run(self):
        list_url_format = 'http://www.chictr.org.cn/searchproj.aspx?title=&officialname=&subjectid=&secondaryid=&applier=&studyleader=&ethicalcommitteesanction=&sponsor=&studyailment=&studyailmentcode=&studytype=0&studystage=0&studydesign=0&minstudyexecutetime=&maxstudyexecutetime=&recruitmentstatus=0&gender=0&agreetosign=&secsponsor=&regno=&regstatus=0&country=&province=&city=&institution=&institutionlevel=&measure=&intercode=&sourceofspends=&createyear=0&isuploadrf=&whetherpublic=&btngo=btn&verifycode=&page={}'
        for i in range(4,50):
            print('当前是第 {} 页'.format(i))
            list_url = list_url_format.format(i)
            # try:
            html = self.downlaoder(list_url)
            detail_urls = self.parser_list(html)
            for detail_url in detail_urls:
                "http://www.chictr.org.cn/showproj.aspx?proj=176272"
                detail_html = self.downlaoder(detail_url)
                page_target_info = self.parse_detail(detail_html)
                item = self.duplicate_(page_target_info,detail_url)
                self.save_data(item)
            # except Exception as e:
            #     time.sleep(60)
            #     logging.info(str(e))
            #     logging.info('有异常跳过, 当前是第 {} 页, 链接地址是: {}'.format(i,list_url))
            #     print('有异常跳过, 当前是第 {} 页, 链接地址是: {}'.format(i,list_url))
        self.close_driver()

if __name__ == '__main__':

    cc = ChiCtr()
    cc.run()