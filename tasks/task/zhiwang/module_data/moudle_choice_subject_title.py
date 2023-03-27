import json
import os

import ddddocr
import requests
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
        pass
        self.session = requests.Session()
        # self.first_moudle_value = '医药'
        # self.first_moudle_value = '感染'
        # self.first_moudle_value = '肿瘤'
        # self.first_moudle_value = '手术'
        # self.first_moudle_value = '心血管'
        # self.first_moudle_value = '糖尿病'
        # self.first_moudle_value = '护理'
        # self.first_moudle_value = '老年'
        # self.first_moudle_value = '基因'
        # self.first_moudle_value = '儿科'
        # self.first_moudle_value = '临床'
        # self.first_moudle_value = '细胞'
        # self.first_moudle_value = '疗效'
        # self.first_moudle_value = '疗效'
        # self.first_moudle_value = '关节'
        # self.first_moudle_value = '病毒'
        # self.first_moudle_value = '重症'
        # self.first_moudle_value = '脑'
        # self.first_moudle_value = '动脉'
    def select_moudle(self):

        self.driver.get('https://www.cnki.net/')
        self.driver.maximize_window()
        time.sleep(2)
        try:
            self.driver.find_element(By.ID, "DBFieldBox").click()
            # 然后选择
            time.sleep(2)
            # span[contains(text(), "指定文本内容")]
            self.driver.find_element(By.XPATH, '//div[@id="DBFieldList"]/ul/li/a[contains(text(),"{}")]'.format(self.first_moudle)).click()
            time.sleep(2)
            self.driver.find_element(By.ID, "txt_SearchText").send_keys(self.first_moudle_value)
            time.sleep(1)
            self.driver.find_element(By.CLASS_NAME, "search-btn").click()
            time.sleep(3)
            self.driver.find_element(By.XPATH, "//li[@data-id='xsqk'][1]").click()
            time.sleep(2)
            self.driver.find_element(By.XPATH, "//li[@data-k='PT'][1]").click()
            time.sleep(2)
            js = "var q=document.documentElement.scrollTop=5000"
            self.driver.execute_script(js)
            # self.driver.find_element(By.XPATH, '//dt[@groupitem="主要主题"]').click()
            time.sleep(3)
            # self.driver.execute_script(js)
            self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//dt[@groupitem="发表年度"]').click()
            time.sleep(2)

        except:
            time.sleep(3)
            self.select_moudle()

    def get_checkcode(self, img):

        ocr = ddddocr.DdddOcr(old=True)
        # 第一个验证截图保存：verification_code_1.png
        with open(img, 'rb') as f:
            image = f.read()
        try:
            res = ocr.classification(image)
        except:
            res = ''
        return res

    def check_code(self):

        # code_url = 'https://kns.cnki.net/kns8/Brief/VerifyCode?t=82283164-b460-420d-9f91-3e402f5714b8&orgin=OverMaxSearchCount'
        # res = self.session.get(code_url)
        for i in range(10):
            self.driver.find_element(By.ID,'changeVercode').screenshot('zw_temp_selenium_code.jpg')
            # with open('zw_temp_selenium_code.jpg', 'wb') as f:
            #     f.write(res.content)
            #     f.close()
            code = self.get_checkcode('./zw_temp_selenium_code.jpg')
            print(code)
            # check_url = 'https://kns.cnki.net/kns8/Brief/CheckCode'
            # data = {
            #     'vericode': code,
            #     'corgin': 'OverMaxSearchCount'
            # }
            # headers = {
            #     "Host": "kns.cnki.net",
            #     "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
            #     "sec-ch-ua-mobile": "?0",
            #     "sec-ch-ua-platform": "\"Windows\"",
            #     "Sec-Fetch-Dest": "document",
            #     "Sec-Fetch-Mode": "navigate",
            #     "Sec-Fetch-Site": "none",
            #     "Sec-Fetch-User": "?1",
            #     "Upgrade-Insecure-Requests": "1",
            #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            # }

            # res = self.session.post(check_url, data=data, headers=headers)
            # print('这是出现临时验证码后的验证结果: ',res.text)
            # if '参数错误' in res.text:
            #     print('临时验证码识别时, 参数错误!!')
            # else:
            #     print('临时验证码验证成功')
            #     return 1
            self.driver.find_element(By.ID,'vericode').send_keys(code)
            time.sleep(2)
            self.driver.find_element(By.ID,'checkCodeBtn').click()
            time.sleep(2)
            print('当前是验证码第 {} 次识别中!!'.format(i))
            if '验证码错误' not in self.driver.page_source:
                print('验证码识别并提交成功!!')
                break
            else:
                print('验证码识别出错, 继续重新识别')
                time.sleep(2)
                self.driver.find_element(By.ID, 'vericode').clear()
                # self.check_code()

    def choice_item(self):
        if os.path.exists(self.path):
            with open(self.path, 'r', encoding='utf-8') as f:
                data = f.read()
        else:
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write('')
            data = None

        if data:
            json_data = json.loads(data)
            print('原数据为: {} '.format(data))
            self.moudle_info = json_data
            max_year = min([int(x) for x in list(json_data.keys())])
        else:
            self.moudle_info = {}
            max_year = self.task['max_year']
        min_year = self.task['min_year']

        # 遍历年限
        for year in range(max_year, min_year, -1):
            print('当前获取的是 {} 年的数据...'.format(year))
            time.sleep(2)
            year = str(year)
            if not year in self.moudle_info:
                self.moudle_info[year] = []
            self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
            # if '提交' in self.driver.page_source:
            #     self.check_code()
            time.sleep(3)
            if '提交' in self.driver.page_source:
                self.check_code()
            time.sleep(3)
            # 选择学科
            cur_html = self.driver.page_source
            html = etree.HTML(cur_html)
            subject_items = html.xpath('//dd[@tit="学科"]//li/input/@text')
            print('原始模块为: {}'.format(subject_items))
            # all_subject_name = for subject_name in self.moudle_info.values()
            if self.moudle_info[year]:
                print('截取开始抓取的学科模块')
                for_strart_subject = self.moudle_info[year][-1]['subject_info']['subject_name']
                print(for_strart_subject)
                strat_index = subject_items.index(for_strart_subject) + 1
                print(strat_index)
                subject_items = subject_items[strat_index:]
                print('截取后学科模块为: {}'.format(str(subject_items)))
            # 遍历学科
            for subject_item in subject_items:
                # if subject_item in
                print('当前是 {} 年, 学科为: {} '.format(year, subject_item))

                try:
                    sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
                    # 点击选项
                    sub_item.click()
                except:
                    if '提交' in self.driver.page_source:
                        self.check_code()
                    jiantou = self.driver.find_element(By.XPATH, '//dl[@groupid="2"]/@class"]')
                    if jiantou and jiantou == 'is-up-fold off':
                        print('此时学科向下的箭头是关闭的, 现在需要点击一下')

                    # 点击向上的按钮， 拉开学科被掩盖的模块内容
                    try:
                        self.driver.find_element(By.XPATH, '//dd[@tit="学科"]//a[@class="btn"]').click()
                        time.sleep(2)
                        if '提交' in self.driver.page_source:
                            self.check_code()
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
                        if '提交' in self.driver.page_source:
                            self.check_code()
                        # print('当前页面 学科 出现了空白, 等待3秒钟, 重新点击 年 释放年, 之后再次发起正常点击')
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
                    if '提交' in self.driver.page_source:
                        self.check_code()

                time.sleep(3)
                html_data = self.driver.page_source
                parse_html = etree.HTML(html_data)
                main_titles = parse_html.xpath('//dl[@groupid="1"]/dd[1]//li/input/@text')
                title_data = [{'title_type':'主要主题','title_text':x} for x in main_titles]
                # print(main_titles)
                minor_titles = parse_html.xpath('//dl[@groupid="2"]/dd[1]//li/input/@text')
                title_data.extend([{'title_type': '次要主题', 'title_text': x} for x in minor_titles])
                # print(title_data)
                # print('这是要看的结果',{x['title_type'] + '__' + x['title_text'] : x for x in title_data})
                title_data_dict = {x['title_type'] + '__' + x['title_text'] : x for x in title_data}
                # print(main_titles)
                # study_level_field = parse_html.xpath('//dd[@tit="研究层次"]/@field')[0].strip()
                # study_lis = parse_html.xpath('//dd[@tit="研究层次"]//li')
                cur_subject_item = {}
                cur_subject_item['title_info'] = title_data_dict
                cur_subject_item['subject_info'] = {}
                subject_field = parse_html.xpath('//dd[@tit="学科"]/@field')[0].strip()
                cur_subject_item['subject_info']['field'] = subject_field
                subject_value = parse_html.xpath('//input[@text="{}"]/@value'.format(subject_item))[0].strip()
                cur_subject_item['subject_info']['value'] = subject_value
                cur_subject_item['subject_info']['subject_name'] = subject_item
                # for study_li in study_lis:
                #     key = study_li.xpath('./input/@text')[0].strip()
                #     value = study_li.xpath('./input/@value')[0].strip()
                #     cur_subject_item['study_level'][key] = {}
                #     cur_subject_item['study_level'][key]['value'] = value
                #     cur_subject_item['study_level'][key]['study_level_field'] = study_level_field
                #     cur_subject_item['study_level'][key]['study_level_name'] = key
                #     time.sleep(3)

                # 取消选项
                sub_item = self.driver.find_element(By.XPATH,'//dd[@tit="学科"]//li/input[@text="{}"]'.format(subject_item))
                sub_item.click()
                if '提交' in self.driver.page_source:
                    self.check_code()
                time.sleep(3)
                self.moudle_info[year].append(cur_subject_item)
                print(self.moudle_info)
                with open(self.path, 'w', encoding='utf-8') as f:
                    f.write(json.dumps(self.moudle_info, ensure_ascii=False))
                    f.close()
            # 释放当前年, 进入下一年
            js = "var q=document.documentElement.scrollTop=3000"
            self.driver.execute_script(js)
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//input[@text="{}"]'.format(year)).click()
            if '提交' in self.driver.page_source:
                self.check_code()
            print('{}年数据已经抓完,进入下一年'.format(year))
            time.sleep(5)
            # time.sleep(10)
            # target = self.driver.find_element_by_xpath('//li/input[@text="{}"]'.format(year))  # 需要将滚动条拖动至的指定的元素对象定位
            # self.driver.execute_script("arguments[0].scrollIntoView();", target)  # 将滚动条拖动到元素可见的地方
            # 选择每一年
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.moudle_info, ensure_ascii=False))
                f.close()
    def run(self):
        # try:

        # self.first_moudle = '文献来源'
        self.first_moudle = '篇名'
        self.first_moudle_value = '医药'
        with open('./zw_tasks_config.json', 'r', encoding='utf-8') as f:
            tasks = json.loads(f.read())

        for task in tasks:
            if task['module_ok'] == 'no':
                self.task = task
                self.driver = webdriver.Chrome()
                self.first_moudle = task['platform']
                self.first_moudle_value = task['keywords']
                self.path = './{}/{}_{}.json'.format(task['module_dir'],task['module_dir'],self.first_moudle_value)
                self.select_moudle()
                self.choice_item()
                self.driver.quit()
            # self.driver.close()
        # except Exception as e:
        #     print('出错写入数据!!')
        #     print(repr(e))
        #     time.sleep(100)
            # self.driver.close()
        #     self.run()
        # with open(self.path, 'w', encoding='utf-8') as f:
        #     f.write(json.dumps(self.moudle_info, ensure_ascii=False))


if __name__ == '__main__':
    m_c = MoudleChoice()
    m_c.run()

