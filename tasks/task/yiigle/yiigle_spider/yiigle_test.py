import json
import os
import random
import re
import time
import urllib.parse
from datetime import datetime
from urllib import parse
from task.chinesejournal.cur_identify import CurIdentify
from lxml import etree
from task.yiigle.loginfromtsg_yiyao import LoginTrun
from task.SqlSave.mongo_store import MongoStore


class Yiigle():

    def __init__(self):

        self.login_obj = LoginTrun()
        self.session = self.login_obj.login_page_turn()
        self.search_keywords = '糖尿病'
        # item 用于存储每篇文章的目标信息, 最后存入到数据库
        self.item = {}

    def get_page_list(self, page):

        list_url = 'http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/apiVue/search/searchList?vpn-12-o2-www.yiigle.com'
        header_list = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "174",
            "Content-Type": "application/json;charset=UTF-8",
            # "Cookie": "wengine_vpn_ticketwebvpn_sdu_edu_cn=7b903bb145120176; refresh=1; refresh=0; session_token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY3MzI0NTAxOCwiZXhwIjoxNjczMjQ4NjE4fQ.eyJ1c2VybmFtZSI6IjcxMDE0Mjg5In0.WDKvuncddwia1X7i8ixm9_-7MFDoHJFVGM0sAc-Gkxh2LsfEQdM49reEkwa2xI2QGtEdtCLCeveA58gOKuLvBw",
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Origin": "http://sdu.webvpn.jingshi2015.com:8383",
            "Referer": "http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/Paper/Search?type=&q={}".format(
                self.search_keywords).encode(),
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        }
        data = '{{"type":"","sortField":"artPubDate","page":{page},"searchType":"pt","pageSize":10,"queryString":"{search_keywords}","query":"","searchText":"{search_keywords}","searchLog":"{search_keywords}","isAggregations":"N"}}'.format(
            search_keywords=self.search_keywords, page=page).encode()

        res = self.session.post(list_url, data=data, headers=header_list)
        print(res.text)
        if res.status_code == 200:
            list_items = res.json()['data']['result']['infos']
            for item in list_items:
                art_id = item['artId']
                pdf_id = self.get_pdf_id(art_id)
                res = self.down_pdf(art_id, pdf_id)
                # http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e2e40f852e396f5c7b468aa395/CN114015202212/1436709.htm
                channelPath = item['channelPath']
                detail_url = 'http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e2e40f852e396f5c7b468aa395/{}/{}.htm'.format(channelPath,art_id)
                artTitle = item['artTitle']
                # print(res.text)

    def get_pdf_id(self, art_id):

        url = 'http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/apiVue/transaction?vpn-12-o2-www.yiigle.com'

        headers = {
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Connection": "keep-alive",
            "Content-Length": "52",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "token": "[object Object]",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "http://sdu.webvpn.jingshi2015.com:8383",
            "Referer": "http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/Paper/Search?type=&q={}&searchType=pt".format(
                self.search_keywords).encode(),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        data = {"productId": art_id, "ProductType": "Tesis", "type": 2}
        res = self.session.post(url, data=json.dumps(data), headers=headers)
        if res.status_code == 200:
            res_data = res.json()['data']
            pdf_id = res_data['token']
        else:
            print('获取pdf_id出现问题, 重新请求并获取pdf_id')
            time.sleep(random.uniform(0, 1))
            return self.get_pdf_id(art_id)
        return pdf_id

    def down_pdf(self, art_id, pdf_id):

        # url = 'http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/apiVue/file/down/1442639/pdf/80cf6f04-149a-4044-9e55-08999303e953'
        url = 'http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/apiVue/file/down/{}/pdf/{}'.format(
            art_id, pdf_id)
        headers = {
            "Host": "sdu.webvpn.jingshi2015.com:8383",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Referer": "http://sdu.webvpn.jingshi2015.com:8383/https-443/77726476706e69737468656265737421e7e056d23e396157720dc7af9758/Paper/Search?type=&q={}&searchType=pt".format(
                self.search_keywords).encode(),
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }
        res = self.session.get(url, headers=headers)
        print('pdf文件数据为: ', res.text)

    def run(self):
        print(self.session.cookies)
        self.get_page_list(2)
        # self.get_pdf_id()
        # self.down_pdf()
        pass
