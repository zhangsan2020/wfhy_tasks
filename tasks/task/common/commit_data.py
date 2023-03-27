
import time
from datetime import datetime

import pymongo
import pandas as pd

class CommitData():

    def __init__(self):

        self.mongo_cli = pymongo.MongoClient(host='47.93.86.81', port=27017,
                                             maxConnecting=1000, authSource='wfhy_commit', username='zl',
                                             password='jiamianwuke2018')
        self.col_min_total = 5
        self.dir_path = 'C:/Users/hello/Desktop/commit_data'

    def update_commit_status(self):

        now_date = datetime.now().strftime('%Y%m%d%H%M%S')
        self.col.update_many({'$and': [{'commit_status': '未提交'}, {'spider_date': {'$lt': now_date}}]},
                        {'$set': {'commit_status': '已提交'}})
        print('更改完成!!')
    def to_excel(self,pdf_col,name):

        # 导出Excel数据
        df = pd.DataFrame(list(self.col.find({'commit_status': '未提交'})))
        # print(df)
        if not df.empty and df.shape[0] > self.col_min_total:
            get_date = datetime.now().strftime('%Y%m%d')
            df.to_excel('{}/{}_{}.xlsx'.format(self.dir_path, name, get_date))
            print('{} 共 {} 条数据,导出完成!!'.format(pdf_col, df.shape[0]))
            self.total_num += df.shape[0]
            # print('5 秒后开始更新 commit_status 状态!!')
            # time.sleep(5)
            # self.update_commit_status(col)
        else:
            print('{}_{} 表中 未提交 数据仅 {} 条, 不足 {} ,不再导出!!'.format(name, pdf_col, df.shape[0], self.col_min_total))

    def get_data(self):
        # '''
        # 功能1 简单清洗pdf网站 16 开头手机号
        # 功能2 将所有清洗过的数据通过放到桌面 C:\Users\hello\Desktop\commit_data 目录里头
        # 功能3 对于导出的数据, 将commit_status更改为 已提交
        # :return:
        #
        # '''
        # 所有表
        pdf_cols = {'zw_commit':'中国知网','wp_commit':'维普网','chinasw_commit':'中国生物医学','yii_commit':'中华医学会'}
        common_cols = {'chaoxing_commit':'超星数据库','chictr_commit':'chictr临床登记平台','chinadrug_commit':'chinadrug药物临床试验','cme_commit':'cme国家级项目网','hbwsrc_commit':'湖北继续教育网'}
        no_update = ['wp_commit','yii_commit','zw_commit']
        self.total_num = 0
        for pdf_col,name in pdf_cols.items():
            self.col = self.mongo_cli['wfhy_commit'][pdf_col]
            self.col.delete_many({'$and':[{'phones':{'$regex':'^16'}},{'commit_status':'未提交'}]})
            print('{} 中开头为 16 的手机号清洗完成!!'.format(pdf_col))
            self.to_excel(pdf_col,name)
            if pdf_col not in no_update:
                self.update_commit_status()
        print('pdf类型数据共导出 {} 条'.format(self.total_num))
        for pdf_col,name in common_cols.items():
            self.col = self.mongo_cli['wfhy_commit'][pdf_col]
            self.to_excel(pdf_col,name)
            if pdf_col not in no_update:
                self.update_commit_status()
        print('本次共导出数据 {} 条'.format(self.total_num))
if __name__ == '__main__':

    commit = CommitData()
    commit.get_data()