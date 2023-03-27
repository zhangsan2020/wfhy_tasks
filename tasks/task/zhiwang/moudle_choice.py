import json
from lxml import etree
from selenium import webdriver
import time
from selenium.webdriver.common.by import By


class MoudleChoice():

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.first_moudle = '参考文献'
        self.first_moudle_value = '病例'

    def select_moudle(self):

        self.driver.get('https://www.cnki.net/')
        self.driver.maximize_window()
        time.sleep(2)
        self.driver.find_element(By.ID, "DBFieldBox").click()
        # 然后选择
        time.sleep(2)

        try:
            # span[contains(text(), "指定文本内容")]
            self.driver.find_element(By.XPATH, '//div[@id="DBFieldList"]/ul/li/a[contains(text(),"{}")]'.format(self.first_moudle)).click()
            time.sleep(2)
            self.driver.find_element(By.ID, "txt_SearchText").send_keys(self.first_moudle_value)
            time.sleep(1)
            self.driver.find_element(By.CLASS_NAME, "search-btn").click()
            time.sleep(3)
            self.driver.find_element(By.XPATH, "//li[@data-id='xsqk'][1]").click()
            time.sleep(2)
            js = "var q=document.documentElement.scrollTop=5000"
            self.driver.execute_script(js)
            self.driver.find_element(By.XPATH, '//dt[@groupitem="主要主题"]').click()
            time.sleep(3)
            self.driver.execute_script(js)
            self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//dt[@groupitem="发表年度"]').click()
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//dt[@groupitem="研究层次"]').click()
            time.sleep(3)

        except:
            time.sleep(3)
            self.select_moudle()

    def choice_item(self):

        with open('old_参考文献_病例.json', 'r', encoding='utf-8') as f:
            data = f.read()
        if data:
            json_data = json.loads(data)
            print('原数据为: {} '.format(data))
            self.moudle_info = json_data
            max_year = min([int(x) for x in list(json_data.keys())])
        else:
            self.moudle_info = {}
            max_year = 2022
        min_year = 2014

        # 遍历年限
        for year in range(max_year, min_year, -1):
            print('当前获取的是 {} 年的数据...'.format(year))
            time.sleep(2)
            year = str(year)
            if not year in self.moudle_info:
                self.moudle_info[year] = {}
            self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
            time.sleep(3)
            # 选择学科
            cur_html = self.driver.page_source
            html = etree.HTML(cur_html)
            subject_items = html.xpath('//dd[@tit="学科"]//li/input/@text')
            # 遍历学科
            for subject_item in subject_items:
                # if subject_item in
                print('当前是 {} 年, 学科为: {} '.format(year, subject_item))

                try:
                    sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
                    # 点击选项
                    sub_item.click()
                except:
                    # 点击向上的按钮， 拉开学科被掩盖的模块内容
                    try:
                        self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
                    except:
                        '''
                        这种做法将是自动切换从头开始再来操作一遍
                        '''
                        # print('当前页面 学科 出现了空白, 等待3秒钟, 重新点击 年 释放年, 之后再次发起正常点击')
                        # time.sleep(3)
                        # # 释放年
                        # print('开始释放年: {}'.format(year))
                        # self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
                        # time.sleep(3)
                        # # 释放年
                        # print('再次点击年: {}'.format(year))
                        # self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
                        # time.sleep(3)
                        # print('点击向下的按钮, 伸开学科, 拿到被覆盖的数据!!')
                        # self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
                        '''
                        测试: 分别点击向上的小箭头, 再次点击向下的小箭头, 获取选项内容
                        '''
                        print('当前页面 学科 出现了空白, 等待3秒钟, 重新点击 年 释放年, 之后再次发起正常点击')
                        time.sleep(3)
                        print('点击发表年度右上角向上箭头!!')
                        self.driver.find_element(By.XPATH,'//dt[@groupitem="发表年度"]/i[@class="icon icon-arrow"]').click()
                        time.sleep(3)
                        print('点击学科右上角向上箭头!!')
                        self.driver.find_element(By.XPATH,'//dt[@groupitem="学科"]/i[@class="icon icon-arrow"]').click()
                        time.sleep(3)
                        print('点击向上的按钮， 拉开学科被掩盖的模块内容!!')
                        self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()

                    time.sleep(3)
                    print('左侧下拉框操作!!')
                    js = 'document.getElementsByClassName("resultlist")[3].scrollTop=2000'
                    self.driver.execute_script(js)
                    time.sleep(2)
                    sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
                    # 点击选项
                    sub_item.click()

                time.sleep(3)
                html_data = self.driver.page_source
                parse_html = etree.HTML(html_data)
                study_level_field = parse_html.xpath('//dd[@tit="研究层次"]/@field')[0].strip()
                study_lis = parse_html.xpath('//dd[@tit="研究层次"]//li')
                self.moudle_info[year][subject_item] = {}
                self.moudle_info[year][subject_item]['study_level'] = {}
                subject_field = parse_html.xpath('//dd[@tit="学科"]/@field')[0].strip()
                self.moudle_info[year][subject_item]['field'] = subject_field
                subject_value = parse_html.xpath('//input[@text="{}"]/@value'.format(subject_item))[0].strip()
                self.moudle_info[year][subject_item]['value'] = subject_value
                for study_li in study_lis:
                    key = study_li.xpath('./input/@text')[0].strip()
                    value = study_li.xpath('./input/@value')[0].strip()
                    # study_level[key] = value
                    self.moudle_info[year][subject_item]['study_level'][key] = {}
                    self.moudle_info[year][subject_item]['study_level'][key]['value'] = value
                    self.moudle_info[year][subject_item]['study_level'][key]['study_level_field'] = study_level_field
                    print(self.moudle_info)
                    time.sleep(3)
                # 取消选项
                sub_item = self.driver.find_element(By.XPATH,
                                                    '//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
                sub_item.click()
                time.sleep(3)

            # 释放当前年, 进入下一年
            js = "var q=document.documentElement.scrollTop=3000"
            self.driver.execute_script(js)
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
            print('{}年数据已经抓完,进入下一年'.format(year))
            time.sleep(5)
            # time.sleep(10)
            # target = self.driver.find_element_by_xpath('//li/input[@text="{}"]'.format(year))  # 需要将滚动条拖动至的指定的元素对象定位
            # self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 将滚动条拖动到元素可见的地方
            # 选择每一年


    def run(self):
        try:
            self.select_moudle()
            self.choice_item()
            with open('old_参考文献_病例.json','w',encoding='utf-8') as f:
                f.write(json.dumps(self.moudle_info,ensure_ascii=False))
            # self.driver.close()
        except Exception as e:
            print('出错写入数据!!')
            print(repr(e))
            with open('old_参考文献_病例.json','w',encoding='utf-8') as f:
                f.write(json.dumps(self.moudle_info,ensure_ascii=False))
            time.sleep(100)
            # self.driver.close()
            self.run()


if __name__ == '__main__':
    m_c = MoudleChoice()
    m_c.run()

