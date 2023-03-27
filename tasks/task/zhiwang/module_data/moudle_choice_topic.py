import json
import os
import re

from lxml import etree
from selenium import webdriver
import time
from selenium.webdriver.common.by import By


class MoudleChoice():

    def __init__(self):

        '''
        获取指定的搜索模块, 本文件获取 年-学科-研究层次
        只需更改 first_moudle, 与first_moudle_value
        '''
        self.driver = webdriver.Chrome()
        self.first_moudle = '主题'
        self.first_moudle_values = ['病','病例','医药','医学','肿瘤']

    def select_moudle(self,moudle_value):

        self.driver.get('https://www.cnki.net/')
        self.driver.maximize_window()
        time.sleep(2)
        try:
            self.driver.find_element(By.ID, "txt_SearchText").send_keys(moudle_value)
            time.sleep(1)
            # print(self.driver.page_source)
            html = self.driver.page_source

        except:
            time.sleep(3)
            html = self.select_moudle(moudle_value)
        return html

    def get_moudles(self,moudle_value,html_data):

        moudles = []
        html = etree.HTML(html_data)
        lis_text = html.xpath('//div[@id="sugtip_ULlist"]/ul/li/@onmouseover')
        for li_text in lis_text:
            moudle = {}
            name = re.findall("this,false,'(.*?)',",li_text)[0]
            moudle['name'] = name
            moudle['search_origin'] = moudle_value
            moudles.append(moudle)
            # print(moudles)
        return moudles
        pass
        # if os.path.exists('old_unit_hospital_sub_origin.json'):
        #     with open('old_unit_hospital_sub_origin.json', 'r', encoding='utf-8') as f:
        #         data = f.read()
        # else:
        #     with open('old_unit_hospital_sub_origin.json', 'w', encoding='utf-8') as f:
        #         pass
        #     data = None
        #
        # if data:
        #     json_data = json.loads(data)
        #     print('原数据为: {} '.format(data))
        #     self.moudle_info = json_data
        #     max_year = min([int(x) for x in list(json_data.keys())])
        # else:
        #     self.moudle_info = {}
        #     max_year = 2022
        #
        # min_year = 2014
        #
        # # 遍历年限
        # for year in range(max_year, min_year, -1):
        #     print('当前获取的是 {} 年的数据...'.format(year))
        #     time.sleep(2)
        #     year = str(year)
        #     if not year in self.moudle_info:
        #         self.moudle_info[year] = []
        #     self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
        #     time.sleep(3)
        #     # 选择学科
        #     cur_html = self.driver.page_source
        #     html = etree.HTML(cur_html)
        #     subject_items = html.xpath('//dd[@tit="学科"]//li/input/@text')
        #     print('原始模块为: {}'.format(subject_items))
        #     # all_subject_name = for subject_name in self.moudle_info.values()
        #     if self.moudle_info[year]:
        #         print('截取开始抓取的学科模块')
        #         for_strart_subject = self.moudle_info[year][-1]['subject_info']['subject_name']
        #         print(for_strart_subject)
        #         strat_index = subject_items.index(for_strart_subject) + 1
        #         print(strat_index)
        #         subject_items = subject_items[strat_index:]
        #         print('截取后学科模块为: {}'.format(str(subject_items)))
        #     # 遍历学科
        #     for subject_item in subject_items:
        #         # if subject_item in
        #         print('当前是 {} 年, 学科为: {} '.format(year, subject_item))
        #
        #         try:
        #             sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
        #             # 点击选项
        #             sub_item.click()
        #         except:
        #             # 点击向上的按钮， 拉开学科被掩盖的模块内容
        #             try:
        #                 self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
        #             except:
        #                 '''
        #                 这种做法将是自动切换从头开始再来操作一遍
        #                 '''
        #                 # print('当前页面 学科 出现了空白, 等待3秒钟, 重新点击 年 释放年, 之后再次发起正常点击')
        #                 # time.sleep(3)
        #                 # # 释放年
        #                 # print('开始释放年: {}'.format(year))
        #                 # self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
        #                 # time.sleep(3)
        #                 # # 释放年
        #                 # print('再次点击年: {}'.format(year))
        #                 # self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
        #                 # time.sleep(3)
        #                 # print('点击向下的按钮, 伸开学科, 拿到被覆盖的数据!!')
        #                 # self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
        #                 '''
        #                 测试: 分别点击向上的小箭头, 再次点击向下的小箭头, 获取选项内容
        #                 '''
        #                 print('当前页面 学科 出现了空白, 等待3秒钟, 重新点击 年 释放年, 之后再次发起正常点击')
        #                 time.sleep(3)
        #                 print('点击发表年度右上角向上箭头!!')
        #                 self.driver.find_element(By.XPATH,'//dt[@groupitem="发表年度"]/i[@class="icon icon-arrow"]').click()
        #                 time.sleep(3)
        #                 print('点击学科右上角向上箭头!!')
        #                 self.driver.find_element(By.XPATH,'//dt[@groupitem="学科"]/i[@class="icon icon-arrow"]').click()
        #                 time.sleep(3)
        #                 print('点击向上的按钮， 拉开学科被掩盖的模块内容!!')
        #                 self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
        #
        #             time.sleep(3)
        #             print('左侧下拉框操作!!')
        #             js = 'document.getElementsByClassName("resultlist")[3].scrollTop=2000'
        #             self.driver.execute_script(js)
        #             time.sleep(2)
        #             sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
        #             # 点击选项
        #             sub_item.click()
        #         time.sleep(3)
        #         html_data = self.driver.page_source
        #         parse_html = etree.HTML(html_data)
        #         origin_field = parse_html.xpath('//dd[@tit="文献来源"]/@field')[0].strip()
        #         origin_lis = parse_html.xpath('//dd[@tit="文献来源"]//li')
        #         cur_subject_item = {}
        #         cur_subject_item['origin_info'] = {}
        #         cur_subject_item['subject_info'] = {}
        #         subject_field = parse_html.xpath('//dd[@tit="学科"]/@field')[0].strip()
        #         cur_subject_item['subject_info']['field'] = subject_field
        #         subject_value = parse_html.xpath('//input[@text="{}"]/@value'.format(subject_item))[0].strip()
        #         cur_subject_item['subject_info']['value'] = subject_value
        #         cur_subject_item['subject_info']['subject_name'] = subject_item
        #         for origin_li in origin_lis:
        #             key = origin_li.xpath('./input/@text')[0].strip()
        #             value = origin_li.xpath('./input/@value')[0].strip()
        #             cur_subject_item['origin_info'][key] = {}
        #             cur_subject_item['origin_info'][key]['value'] = value
        #             cur_subject_item['origin_info'][key]['origin_field'] = origin_field
        #             cur_subject_item['origin_info'][key]['origin_name'] = key
        #             time.sleep(3)
        #             # print(cur_subject_item)
        #         # 取消选项
        #         # js = "var q=document.documentElement.scrollTop=500"
        #         # self.driver.execute_script(js)
        #         sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
        #         sub_item.click()
        #         time.sleep(3)
        #         self.moudle_info[year].append(cur_subject_item)
        #         print(self.moudle_info)
        #         with open('old_unit_hospital_sub_origin.json', 'w', encoding='utf-8') as f:
        #             f.write(json.dumps(self.moudle_info, ensure_ascii=False))
        #     # 释放当前年, 进入下一年
        #     js = "var q=document.documentElement.scrollTop=3000"
        #     self.driver.execute_script(js)
        #     time.sleep(2)
        #     self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
        #     print('{}年数据已经抓完,进入下一年'.format(year))
        #     time.sleep(5)
        #     # time.sleep(10)
        #     # target = self.driver.find_element_by_xpath('//li/input[@text="{}"]'.format(year))  # 需要将滚动条拖动至的指定的元素对象定位
        #     # self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 将滚动条拖动到元素可见的地方
        #     # 选择每一年
        #     with open('old_unit_hospital_sub_origin.json', 'w', encoding='utf-8') as f:
        #         f.write(json.dumps(self.moudle_info, ensure_ascii=False))

    def run(self):


        with open('old_topic.json', 'r', encoding='utf-8') as f:
            data = f.read()
        if data:
            self.moudle_json = json.loads(f.read())
        else:
            self.moudle_json = {}
            self.moudle_json['model'] = '主题'
            self.moudle_json['keywords'] = {}
        for moudle_value in self.first_moudle_values:
            if not self.moudle_json['keywords'].get(moudle_value):
                html = self.select_moudle(moudle_value)
                item_list = self.get_moudles(moudle_value,html)
                self.moudle_json['keywords'][moudle_value] = item_list
                print(self.moudle_json)
                print('当前搜索模块已拿到, 进入下一模块!!!')
                with open('old_topic.json', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(self.moudle_json,ensure_ascii=False))
            else:
                print('当前模块之前已经抓取过, 进入下一模块!!')

        # try:
        # self.select_moudle()
        # self.choice_item()
            # self.driver.close()
        # except Exception as e:
        #     print('出错写入数据!!')
        #     print(repr(e))
        #     time.sleep(100)
        #     # self.driver.close()
        #     self.run()
        # with open('old_unit_hospital_sub_study.json', 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(self.moudle_info, ensure_ascii=False))

if __name__ == '__main__':
    m_c = MoudleChoice()
    m_c.run()

