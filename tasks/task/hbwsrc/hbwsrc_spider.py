from datetime import datetime
import json
import random
import re
import time
import hashlib
import requests
from ..common.useragent import useragent_pool
from .hbw_redis import HbRedis
from ..SqlSave.mongo_store import MongoStore


class HbwSrc():

    def __init__(self):

        self.md5_ = hashlib.md5()
        self.retry_detail_max = 5
        self.page_size = 150
        self.redis_cli = HbRedis()
        self.mongo_client_all = MongoStore('wfhy_update', 'hbwsrc_all')
        self.mongo_client_commit = MongoStore('wfhy_commit', 'hbwsrc_commit')
        self.item = {}

    def get_sign(self):

        cur_time = int(time.time() * 1000)
        data = "curefunCase" + hex(cur_time)[2:] + '/teachcredit/project/qryProjectPublished'
        self.md5_.update(data.encode())
        sign = self.md5_.hexdigest()
        t_sign = 't=' + str(cur_time) + '&sign=' + sign
        print(t_sign)
        return t_sign

    def post_url(self, page_num, year):
        for i in range(self.retry_detail_max):
            t_sign = self.get_sign()
            # http://cme.hbwsrc.cn//teachcredit/project/qryProjectPublished?t=1662348532449&sign=3b7e97ad5da95bb490facfb0d7b66014&token=&device_type=1
            # http://cme.hbwsrc.cn//teachcredit/project/qryProjectPublished?t=1662350500825&sign=3f37b8256e844ed822d6d95b45053548&token=&device_type=1
            # http://cme.hbwsrc.cn//teachcredit/project/qryProjectPublished?t=1679294426131&sign=16f4fc281cb246bbb345ad0e7781d477&token=&device_type=1
            list_url = 'http://cme.hbwsrc.cn//teachcredit/project/qryProjectPublished?t=1679294426131&sign={}&token=&device_type=1'.format(
                t_sign)
            data = {"page_num": page_num, "page_size": self.page_size, "declare_company": "", "credit_level": "",
                    "the_subject": "",
                    "the_third_subject": "", "project_leader": "", "hold_year": year, "simulation_place": "",
                    "simulation_time": "",
                    "actual_credits": "", "credit_awarded": "", "is_open_class": "-1"}
            headers = {
                "User-Agent": random.choice(useragent_pool),
                "Content-Type": "application/json;charset=UTF-8",
                "Referer": "http://cme.hbwsrc.cn/conEducation_front/template/list/travel.html",
                "Host": "cme.hbwsrc.cn",
                "Origin": "http://cme.hbwsrc.cn",
                # "Content-Length": "249",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive"

            }
            try:
                res = requests.post(list_url, data=json.dumps(data), headers=headers,timeout=(20,30))
            except Exception as e:
                print('请求列表页出现异常,重新请求, 跳过!!')
                continue
            time.sleep(random.uniform(0, 1))
            if res.status_code == 200 and 'data' in res.json():
                # print(res.json())
                return res.json()
            else:
                print('当前列表页第 {} 次获取异常'.format(i))
                time.sleep(random.uniform(30,60))
                if i >= 3:
                    print('当前列表页超过 3 次获取异常,休息5分钟,再次抓取!!'.format(i))
                    time.sleep(300)

    def get_item(self, detail_id):

        for i in range(self.retry_detail_max):
            t_sign = self.get_sign()
            # 'http://cme.hbwsrc.cn/teachcredit/project/queryProjectData/20220326100000095?t=1662356440588&sign=7537443dafea7a612c89c9be67599a3f&token=&device_type=1'
            # http://cme.hbwsrc.cn/teachcredit/project/queryProjectData/20220315100000905?t=1679297415609&sign=c8d4032108eccbb1c6ea8a216a47e282&token=&device_type=1
            url = 'http://cme.hbwsrc.cn/teachcredit/project/queryProjectData/{}?t=1679297415609&sign={}&token=&device_type=1'.format(detail_id,
                                                                                                                t_sign)
            headers = {
                "User-Agent": random.choice(useragent_pool),
                # "Content-Type": "application/json;charset=UTF-8",
                "Referer": "http://cme.hbwsrc.cn/conEducation_front/template/list/travel.html",
                "Host": "cme.hbwsrc.cn",
                # "Origin": "http://cme.hbwsrc.cn",
                # "Content-Length": "249",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive"

            }
            try:
                res = requests.get(url, headers=headers,timeout=(20,30))
            except Exception as e:
                print('详情链接获取出现问题,详情为: {}, 等待一会儿重新获取!!'.format(str(e)))
                time.sleep(60)
                continue
            time.sleep(random.uniform(0, 1))
            if res.json() and res.json()['data']:
                json_data = res.json()['data']
                self.item.clear()
                self.item['name'] = json_data['project_leader']
                self.item['phone'] = json_data['project_leader_phone']
                self.item['leader_title'] = json_data['project_leader_title']
                self.item['detail_url'] = url
                break
            elif res.json() and res.json()['data'] == None:
                print('当前页面无数据,链接地址为: {}, 重新获取数据'.format(url))
                time.sleep(random.uniform(10,20))
                if i >= 3:
                    print('第三次获取数据异常,等待一会儿, 重新获取!!')
                    time.sleep(random.uniform(300, 600))
            else:
                print(res.text)
                print('详情页数据第 {} 次获取出现异常! 即将重新发起请求!!'.format(i))
                time.sleep(random.uniform(10,20))
                if i >= 3:
                    print('第三次获取数据异常,等待一会儿, 重新获取!!')
                    time.sleep(random.uniform(300,600))

    def parse_max_page(self, year, page_num=1):

        json_datas = self.post_url(1, year)
        totalCount = json_datas['data']['totalCount']
        maxpage = totalCount // self.page_size + 1
        return maxpage

    def duplicate_store(self):

        self.item['spider_date'] = datetime.now().strftime('%Y%m%d%H%M')
        if re.findall('1[\d+]{10}',self.item['phone']):
            status = self.redis_cli.set_item('hbwsrc', self.item['phone'])
            if status == 1:
                print('发现新手机号, 插入commit表中!!')
                self.item['commit_status'] = '未提交'
                self.mongo_client_commit.insert(self.item)
            elif status == 0:
                print('检测到之前已经抓取过当前数据, 不再插入commit表中!!')
            else:
                print('redis去重出现了问题, 请仔细查阅!!')
        self.mongo_client_all.insert(self.item)
        self.item.clear()

    def run(self):
        years = [2021, 2020, 2019, 2018]
        # years = [2017]

        for year in years:
            self.item['cur_year'] = year
            maxpage = self.parse_max_page(year) + 1
            print('{}年最大页码是: {}'.format(year, maxpage))
            for page_num in range(1, maxpage):
                print('当前是 {} 年 第 {} 页数据'.format(year,page_num))

                time.sleep(5)
                page_json = self.post_url(page_num, year)
                items = page_json['data']['list']
                for item_data in items:
                    detail_id = item_data['project_id']
                    time.sleep(random.uniform(0,1))
                    print('***'*10)
                    self.get_item(detail_id)
                    print('这是获取到的item: ',self.item)
                    self.item['cur_page'] = page_num
                    self.duplicate_store()
                    print('***'*10)




if __name__ == '__main__':
    hb = HbwSrc()
    hb.get_sign()
