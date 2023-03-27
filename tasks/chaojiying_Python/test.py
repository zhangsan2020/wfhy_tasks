import time
from PIL import Image
import pytesseract
from os import path
from chaojiying import Chaojiying_Client
from lxml import etree
import csv
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
# url = 'https://cmegsb.cma.org.cn/national_project/projectGongbuList.do'
#
# res = requests.post()
#
class CmegSb():

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get('https://cmegsb.cma.org.cn/national_project/listBaseProjectGongbu.jsp')
        self.driver.implicitly_wait(5)

    def select_year(self,year):
        select = Select(self.driver.find_element_by_id('year'))
        # 然后选择
        time.sleep(2)
        select.select_by_visible_text(year)

    def page_size(self):
        self.driver.find_element_by_id('pageSize').clear()
        self.driver.find_element_by_id('pageSize').send_keys(526)

    # 保存验证码
    def save_imgcode(self):
        self.driver.find_element_by_id('codeImg').screenshot('imgcode.jpeg')

    # 验证码识别
    def get_code(self):
        chaojiying = Chaojiying_Client('1029025432', 'jiamianwuke2018','6e01a48912ce0a49b6dfc72f53bd3875')  # 用户中心>>软件ID 生成一个替换 96001
        im = open('imgcode.jpeg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
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
            item = []
            tds = tr.xpath('./td')
            item.append(tds[5].text)
            item.append(tds[6].text)
            items.append(item)
        return items

    def save_data(self,items):

        with open('cmegsb_2022.csv','w',encoding='utf-8',newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['姓名', '电话'])
            writer.writerows(items)


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