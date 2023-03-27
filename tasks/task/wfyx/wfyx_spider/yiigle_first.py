import json
import random
import re
import time
from datetime import datetime
from task.chinesejournal.cur_identify import CurIdentify
from task.yiigle.login_tsg90 import LoginTrun
from task.SqlSave.mongo_store import MongoStore
from task.yiigle.redis_yii import YiRedis
from ..cur_identify import CurIdentify


class Yiigle():

    def __init__(self):

        self.spider_at = 'win'
        self.mode = '全库'
        self.identify = CurIdentify()
        self.login_obj = LoginTrun()
        self.session, self.login_data = self.login_obj.login_page_turn('90tsg')
        # self.search_keywords = '糖尿病'
        self.search_keywords = '细胞'
        self.tasks_path = './task/yiigle/yiigle_config.json'
        self.dir_pdfs = 'F:/yixuehui_pdfs'
        self.mongo_yii_all = MongoStore('wfhy_update', 'yii_all')
        self.mongo_yii_commit = MongoStore('wfhy_commit', 'yii_commit')
        self.redis_yii = YiRedis()
        self.get_search_info()
        # item 用于存储每篇文章的目标信息, 最后存入到数据库
        self.item = {}
        self.retry_down_pdf_max = 3
        self.retry_down_list_max = 5
        self.down_pdffail_num = 0
        self.list_fail_num = 0


    def update_task(self, condition, **kwargs):

        mode = condition['mode']
        keywords = condition['keywords']
        max_year = condition['max_year']
        min_year = condition['min_year']
        with open(self.tasks_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        for index, search_info in enumerate(json_data):
            if search_info['mode'] == mode and search_info['keywords'] == keywords and search_info[
                'max_year'] == max_year and search_info['min_year'] == min_year:
                print(mode, keywords, kwargs)
                json_data[index].update(kwargs)
                print('这是更新后的json_data!!!')
        with open(self.tasks_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(json_data, ensure_ascii=False))
            f.close()

    def get_search_info(self):

        with open(self.tasks_path, 'r', encoding='utf-8') as f:
            json_data = json.loads(f.read())
            f.close()
        new_list = []
        for search_info in json_data:
            if search_info['have_end'] != 1 and search_info['is_running'] != 1 and search_info['spider_at'] == self.spider_at and search_info['mode'] == self.mode:
                new_list.append(search_info)
        if new_list:
            sorted_list = sorted(new_list, key=lambda x: x['level'], reverse=False)
            print('这是排序中的sorted_list', sorted_list)
            self.search_info = sorted_list[0]
            # self.update_task(self.search_info,have_start=1,is_running=1)

        else:
            print('任务都已经都在运行中/已完成了, 请注意查看并添加新的任务!!!')
            exit()

    def get_page_num(self, year):

        list_url = 'http://yiigle.meddata.d.jd314.vip/getCore/manyElements'
        header_list = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "479",
            "Content-Type": "application/json",
            # "Cookie": "Hm_lvt_04b5e4d6892791247a01f35935d692be=1670286856,1670291708,1670375260,1672812177; _trs_uv=lco916ox_5355_2ja3; authdomain=AuthDomain.tsg211.com",
            "electronicPublicationStatus": "0",
            "Host": "yiigle.meddata.d.jd314.vip",
            "Origin": "http://yiigle.meddata.d.jd314.vip",
            "Referer": "http://yiigle.meddata.d.jd314.vip/",
            "token": "{}".format(self.login_data['data']['loginName']),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

        data = {
            "pageNo": 1,
            "pageSize": self.search_info['page_size'],
            "condition": {
                "main": "{}".format(self.search_info['keywords']),
                "author": "",
                "authorCom": "",
                "periodicalName": "",
                "yearStage": "",
                "yearList": [str(year)],
                "journalTypeList": [],
                "sorting": "发表时间",
                # "retrieve": " (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1"
            }
        }

        res = self.session.post(list_url, data=json.dumps(data), headers=header_list,timeout=(20,30))
        res.encoding = 'utf-8'
        if res.status_code == 200:
            max_page = res.json()['pages']
            total = res.json()['total']
            print('当前模块含有文章 {} 页, 共 {} 条'.format(max_page, total))
            return max_page
        else:
            print("获取列表页页码失败, 重新获取!!")
            time.sleep(random.uniform(2,5))
            self.get_page_num(year)

    def get_page_list(self, page, year):

        list_url = 'http://yiigle.meddata.d.jd314.vip/getCore/manyElements'
        header_list = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "479",
            "Content-Type": "application/json",
            # "Cookie": "Hm_lvt_04b5e4d6892791247a01f35935d692be=1670286856,1670291708,1670375260,1672812177; _trs_uv=lco916ox_5355_2ja3; authdomain=AuthDomain.tsg211.com",
            "electronicPublicationStatus": "0",
            "Host": "yiigle.meddata.d.jd314.vip",
            "Origin": "http://yiigle.meddata.d.jd314.vip",
            "Referer": "http://yiigle.meddata.d.jd314.vip/",
            "token": "{}".format(self.login_data['data']['loginName']),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

        data = {
            "pageNo": page,
            "pageSize": self.search_info['page_size'],
            "condition": {
                "main": "{}".format(self.search_info['keywords']),
                "author": "",
                "authorCom": "",
                "periodicalName": "",
                "yearStage": "",
                "yearList": [str(year)],
                "journalTypeList": [],
                "sorting": "发表时间",
                # "retrieve": " (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1 AND (titleCN:细胞 OR abstractCN:细胞 OR keywordCN:*细胞*) AND !isChMeAss:\"4\" AND start:1"
            }
        }
        for i in range(self.retry_down_list_max):
            try:
                res = self.session.post(list_url, data=json.dumps(data), headers=header_list,timeout=(20,30))
                res.encoding = 'utf-8'
                if res.status_code == 200:
                    list_items = res.json()['list'][0]['resultList']
                    if len(list_items) > 0:
                        for item in list_items:
                            print('***' * 5 + '发现新数据' + '***' * 5)
                            self.item.clear()
                            self.item['art_id'] = item['id']
                            self.item['detail_url'] = 'http://yiigle.meddata.d.jd314.vip/#/details?id=' + item['id']
                            self.item['date'] = item['pubDate']
                            self.item['title'] = item['titleCN']
                            self.item['file_name'] = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "",
                                                            self.item['title'])
                            md5_str = self.item['file_name'] + self.item['date']
                            status = self.redis_yii.set_item('yii', md5_str)
                            if status == 1:
                                file_path = self.dir_pdfs + '/' + self.item['file_name'] + '_' + self.item[
                                    'date'] + '.pdf'
                                self.item['origin'] = item['periodicalName']
                                self.item['author'] = json.dumps(item['authorList'], ensure_ascii=False)

                                self.item['sitename'] = item['crawlSiteName']
                                self.item['pyear'] = item['pyear']
                                print('这是item: ', item)
                                self.down_pdf(file_path)
                                print('下载路径地址为: {}'.format(file_path))
                                print('开始识别医生信息...')
                                doctor_infos = self.identify.identify_pdf(file_path)
                                print('识别结果为: ', doctor_infos)
                                self.item.update(doctor_infos)
                                print("添加医生信息后的数据为: ", item)
                                self.save(self.item)
                            else:
                                print('已经抓取过当前数据, 不再抓取, 跳过!')
                                continue
                            # print('***' * 5 + '发现新数据' + '***' * 5)
                        break
                    else:
                        print('列表页没有文章数据了!! 可以跳过当前年, 抓取下一年数据!!')
                else:
                    print('列表页第 {} 页下载失败,暂停5秒钟, 重新下载!!'.format(page))
                    time.sleep(random.uniform(3, 10))

            except:
                print('请求列表页第 {} 次 出现问题, 暂停一会儿, 重新发起请求!!'.format(i))
                time.sleep(random.uniform(15,30))
                # res = self.session.post(list_url, data=json.dumps(data), headers=header_list)



    def down_pdf(self, file_path):

        url = 'http://download.meddata.com.cn:8087/getCore/downloadCore?id={}&loginName={}&token={}'.format(
            self.item['art_id'], self.login_data['data']['loginName'], self.login_data['data']['token'])
        self.item['pdf_url'] = url
        headers = {
            "Host": "download.meddata.com.cn:8087",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://yiigle.meddata.d.jd314.vip/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        for i in range(self.retry_down_pdf_max):
            print('开始下载pdf文件...')
            try:
                res = self.session.get(url, headers=headers,timeout=(20,30))
                time.sleep(random.uniform(1,2))
                if res.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(res.content)
                        f.close()
                    print('pdf文件下载完成!!')
                    self.down_pdffail_num = 0
                    break
                else:
                    print('pdf文件下载失败第 {} 次, url 为 {} 信息为: {}, 等待一下重新下载'.format(i,url,file_path))
                    time.sleep(random.uniform(3,5))
            except:
                print('下载pdf文件第 {} 次读取失败或请求出错,不打紧再来!!'.format(i))
        else:
            self.down_pdffail_num += 1
        if self.down_pdffail_num >= 5:
            print('连续5个pdf文件下载失败, 可能遇到反爬, 休息10~15分钟后继续抓取!!')
            time.sleep(random.uniform(600,900))
            self.down_pdffail_num = 0

    def save(self, item):

        spider_date = datetime.now().strftime('%Y%m%d%H%M')
        item['spider_date'] = spider_date
        item['origin_moudle'] = '{}_{}_{}年_{}'.format(self.search_info['mode'], self.search_info['keywords'],
                                                        self.cur_year,self.search_info['spider_at'])
        self.mongo_yii_all.insert(item)
        if ('phones' in item) and item['phones']:
            print('发现新数据, 且存在手机号, 可以插入到commit表中')
            item['commit_status'] = '未提交'
            self.mongo_yii_commit.insert(item)
        else:
            print('检测到新数据, 但手机号为空, 不加入到commit表中')

    def run(self):
        # print(self.session.cookies)

        for year in range(self.search_info['max_year'], self.search_info['min_year'], -1):
            self.cur_year = year
            self.update_task(self.search_info, have_start=1, is_running=1, cur_year=year)
            max_page = self.get_page_num(year) + 1
            for page in range(37,max_page):
                print('当前是 {} {} {}年 第 {} 页数据'.format(self.search_info['mode'], self.search_info['keywords'], year, page))
                self.get_page_list(page, year)
        self.update_task(self.search_info,have_end=1,is_running=0,cur_year=self.cur_year)