import time

import pymongo
from ..common.common_data import mongo_main_info

class MongoStore():

    def __init__(self, db, col):

        self.connect_(db,col)

    def connect_(self,db,col):

        self.mongo_cli = pymongo.MongoClient(host=mongo_main_info['host'], port=mongo_main_info['port'],maxConnecting=1000,authSource=db,username='zl',password='jiamianwuke2018')
        # self.col = self.mongo_cli[db][col]
        self.db = self.mongo_cli[db]
        # self.db.authenticate('zl', 'jiamianwuke2018')
        self.col = self.db[col]

    def insert(self, item):
        try:
            self.col.insert_one(item)
            print('插入mongo成功!!')
        except:
            time.sleep(10)
            self.connect_(self.db,self.col)
            self.insert(item)

    def find_(self, reg=None, sort_field=None, sort_type=1, limit_num=0):
        datas = self.col.find(reg).sort(sort_field,sort_type).limit(limit_num)
        for data in datas:
            yield data
        # return datas

    def find_page_num(self,owning_account,origin_moudle):

        print('获取mongo中页码数据的基本条件为: {}__{}'.format(owning_account,origin_moudle))
        page_num_data = [page_num['cur_page'] for page_num in self.col.find({'$and':[{'owning_account':owning_account},{'origin_moudle':origin_moudle}]}).sort("cur_page",-1).limit(1)]
        # for page_num in page_num_data
        print('mongo中当前已经存储的页码最大值为: ',page_num_data)
        if page_num_data:
            return page_num_data[0]
        else:
            return 0

    def get_module_end_year(self,module_end_year_data):
        reg_data = module_end_year_data + '_over'
        datas = self.col.find({'module_end_year':reg_data}).sort('spider_date',-1).limit(1)
        for data in datas:
            if data:
                print('找到当前年已经抓取完成的标志, 不再进行数据抓取!!')
                return 'cur_year_over'

    def insert_module_end_year(self,reg_end_year_data):

        end_year_value = reg_end_year_data + '_over'
        res_datas = self.col.find({'origin_module':{'$regex':reg_end_year_data}}).sort('spider_date',-1).limit(1)
        for res_data in res_datas:
            print('当前年已经抓取完成,在mongo中添加 module_end_year 标识')
            status = self.col.update_one({'_id':res_data['_id']},{'$set':{'module_end_year':end_year_value}})
            print(status)




#
# if __name__ == '__main__':
#     mongo_cli = MongoStore('wfhy_commit', 'chictr_commit')
#     mongo_cli.find_(sort_field='url_id',sort_type=-1,limit_num=1)
