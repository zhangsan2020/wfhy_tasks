import os
import re
import time
from PIL import Image
import pytesseract
from os import path
from ..chaojiying import Chaojiying_Client
from lxml import etree
from datetime import datetime
import csv
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from openpyxl import Workbook
from ..SqlSave.redis_ import RedisCli
from ..SqlSave.mongo_store import MongoStore
# url = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do'
#
# res = requests.post()
#
class CmegSb():

    def __init__(self):

        self.wb = Workbook()
        self.sheet = self.wb.active
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get('https://cmegsb.cma.org.cn/national_project/listBaseProjectGongbu.jsp')
        self.driver.implicitly_wait(5)
        self.redis_cli = RedisCli()
        self.mongo_cli = MongoStore('wfhy','cmeg')
        self.cur_dir = os.path.dirname(os.path.realpath(__file__))
        self.imgcode_path = self.cur_dir + '\imgs\img_code.jpeg'
        print(os.path.dirname(os.path.realpath(__file__)))
        print(self.imgcode_path)
    def select_year(self,year):
        select = Select(self.driver.find_element_by_id('year'))
        # 然后选择
        time.sleep(2)
        select.select_by_visible_text(year)

    def page_size(self):
        self.driver.find_element_by_id('pageSize').clear()
        self.driver.find_element_by_id('pageSize').send_keys(900)

    # 保存验证码
    def save_imgcode(self):
        print(self.imgcode_path)
        self.driver.find_element_by_id('codeImg').screenshot(self.imgcode_path)

    # 验证码识别
    def get_code(self):
        chaojiying = Chaojiying_Client('1029025432', 'jiamianwuke2018','6e01a48912ce0a49b6dfc72f53bd3875')  # 用户中心>>软件ID 生成一个替换 96001
        im = open(self.imgcode_path, 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        code_data = chaojiying.PostPic(im, 6001)
        return code_data['pic_str']

    def send_imgcode(self):
        self.save_imgcode()
        code_num = self.get_code()
        self.driver.find_element_by_id('J_VCode').send_keys(code_num)
        time.sleep(2)

    def submit(self):
        self.driver.find_element_by_xpath('//input[@type="submit"]').click()

    def get_html_data(self):
        self.driver.switch_to_frame("resultIFrame")
        time.sleep(2)
        html = self.driver.page_source
        # print(driver.page_source)
        return html

    def parser(self,data):

        html = etree.HTML(data)
        # trs = html.xpath('//table[@id="its"]/tbody//trs[not(contains(@id))]')
        trs = html.xpath('//table[@id="project"]/tbody//tr[(@class)]')
        # print(trs)
        items = []

        for tr in trs:
            data_dic = {}

            tds = tr.xpath('./td')
            # 13901391680
            # 010-82195158
            flag = 0
            # 如果其他负责人的电话是手机号获取
            if re.findall('[0-9]{11}',tds[3].text):
                item_line = tds[2].text + tds[3].text
                res = self.redis_cli.set_item('cmeg',item_line)
            # 如果当前项目负责人的电话为手机号也获取
                if res == 1:
                    flag = 1
                    item = []
                    item.append(tds[2].text)
                    item.append(tds[3].text)
                    items.append(item)
                elif res == 0:
                    print('之前已经抓取过且放入到本地redis cmeg键中, 不在存入')
                else:
                    print('存入数据错误!!')
            else:
                print('当前电话 {} 为座机电话, 舍去!!'.format(tds[6].text))
            if re.findall('[0-9]{11}',tds[6].text):
                item_line = tds[5].text + tds[6].text
                res = self.redis_cli.set_item('cmeg',item_line)
            # 如果当前项目负责人的电话为手机号也获取
                if res == 1:
                    flag = 1
                    item = []
                    item.append(tds[5].text)
                    item.append(tds[6].text)
                    items.append(item)
                elif res == 0:
                    print('之前已经抓取过且放入到本地redis cmeg键中, 不在存入')
                else:
                    print('存入数据错误!!')

            else:
                print('当前电话 {} 为座机电话, 舍去!!'.format(tds[6]))
            if flag == 1:
                # 单位
                data_dic['unit'] = tds[1].text
                # 其他负责人
                data_dic['other_leader'] = tds[2].text
                data_dic['other_leader_phone'] = tds[3].text
                data_dic['title'] = tds[4].text
                # 项目负责人
                data_dic['leader'] = tds[5].text
                # 项目负责人手机号
                data_dic['leader_phone'] = tds[6].text
                # 举办期限起止日期
                data_dic['days'] = tds[7].text
                data_dic['place'] = tds[8].text
                # 授予学员学分
                data_dic['score'] = tds[9].text
                # 教学对象
                data_dic['target_stu'] = tds[10].text
                # 拟招生人数
                data_dic['stu_nums'] = tds[11].text
                self.mongo_cli.insert(data_dic)

        return items


    def save_data(self,items):
        if items:
            date = datetime.now().strftime('%Y%m%d%H%m')
            filename = self.cur_dir + '\cmegdata\cmeg数据表_{}.xlsx'.format(date)
            self.sheet.title = 'cmeg网站2022年发布信息'
            self.sheet.append(['姓名','手机号'])
            for item in items:
                self.sheet.append([item[0], item[1]])
            self.wb.save(filename)
            self.wb.close()
            # writer.writerow([item['title'], item['abstract'], item['nickname']])
            # with open('cmegsb_2022.csv','w',encoding='utf-8',newline='') as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerow(['姓名', '电话'])
            #     writer.writerows(items)
        else:
            print('今日cmeg网站无更新数据!')


    def run(self):

        self.select_year('2022')
        self.send_imgcode()
        self.page_size()
        self.submit()
        html = self.get_html_data()
        items = self.parser(html)
        self.save_data(items)


if __name__ == '__main__':

    cme = CmegSb()
    cme.run()