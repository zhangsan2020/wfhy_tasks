#!/usr/bin/env python
import datetime
import pymongo
from task.common.common_data import mongo_main_info
from .sendwx import send

class SpiderMessage():

    def __init__(self):

        # self.connect_()
        # self.cols = ['chaoxing_commit','chinasw_commit']
        self.cols = {'超星期刊':'chaoxing_commit','中国生物医学文献':'chinasw_commit'}
        # self.spider_today_num = 0
        # self.spider_today_num


    def connect_(self,db):

        self.mongo_cli = pymongo.MongoClient(host=mongo_main_info['host'], port=mongo_main_info['port'],maxConnecting=1000,authSource=db,username='zl',password='jiamianwuke2018')
        # self.col = self.mongo_cli[db][col]
        self.db = self.mongo_cli[db]
        # self.col = self.db[col]
        #
    def get_message(self):
        '''
        1 今天共抓取多少条信息
        2 各个网站今天分别抓取多少信息及未提交数据共多少条
        3 图形化展示信息
        :return:
        '''
        now = datetime.datetime.now()
        # 获取今天零点
        temp_zero = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,
                                             microseconds=now.microsecond)
        today_zero = temp_zero.strftime('%Y%m%d%H%M')
        today_now = now.strftime('%Y%m%d%H%M')
        # print(today_zero,today_now)
        self.connect_('wfhy_commit')
        today_spider_sum = 0
        today_spider_detail = '    今日抓取数据详情: \n'
        no_commit_detail = '    未提交总量数据详情: \n'
        no_commit_sum = 0
        for web_name,col_name in self.cols.items():
            today_spider_num = self.db[col_name].count_documents({"spider_date":{"$gte":today_zero,"$lte":today_now}})
            today_spider_sum += today_spider_num
            no_commit_num = self.db[col_name].count_documents({'commit_status':'未提交'})
            # print('{} 今日抓取了 {} 条数据!!'.format(web_name,today_spider_num))
            no_commit_sum += no_commit_num
            # detail_key = '{} 今日抓取条数为: '.format(web_name)
            # today_spider_detail[detail_key] = today_spider_num
            today_spider_detail += '        {} : {} 条\n'.format(web_name,today_spider_num)
            no_commit_detail += '       {} : {} 条\n'.format(web_name,no_commit_num)

        today_spider_detail += '        今日抓取总计 : {} 条\n'.format(today_spider_sum)
        no_commit_detail += '       未提交总计 : {} 条\n'.format(no_commit_sum)
        # print(today_spider_detail)
        # print(no_commit_detail)
        date_today = datetime.date.today().strftime('%Y年%m月%d日')
        message = '{} 数据详情: \n\n'.format(date_today)
        message += today_spider_detail + '\n' + no_commit_detail
        return message

    def send_message(self):
        message = self.get_message()
        print(message)
        send(message)

# if __name__ == '__main__':
#
#     mess = SpiderMessage()
#     mess.get_sql_data()