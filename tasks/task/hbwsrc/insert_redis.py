import pymongo
import redis
import pandas as pd

class InsertData():

    def __init__(self):

        self.mongo_cli = pymongo.MongoClient(host='47.93.86.81', port=27017,
                                             maxConnecting=1000, authSource='wfhy_update', username='zl',
                                             password='jiamianwuke2018')
        # # self.col = self.mongo_cli[db][col]
        # # self.db = self.mongo_cli[db]
        # # # self.db.authenticate('zl', 'jiamianwuke2018')
        # # self.col = self.db[col]
        self.col = self.mongo_cli['wfhy_commit']['hubei_commit']
        self.redis_cli = redis.Redis(host='47.93.86.81', password='jiamianwuke2018',
                                     port=6379, decode_responses=True, health_check_interval=320)

    def find_identify_data(self):

        # fail_datas = self.col.find({'identify_status':'文件过小未下载'})
        # fail_datas = self.col.find({'identify_status':'识别失败'})
        fail_datas = self.col.find({'spider_date':{'$gt':'202302030000'}})
        # success_datas = self.col.find({'identify_status':'识别成功'})
        # success_titles = set()
        # fail_titles = set()
        # for success_data in success_datas:
        #     success_ele = success_data['title']+str(success_data['date'])
        #     success_titles.add(success_ele)
        # print(success_titles)
        # print(len(success_titles))
        for fail_data in fail_datas:
            print(fail_data)
            # filename =fail_data['title']
            file_name = fail_data['file_name'] + fail_data['date']
            md5_str = self.md5_(file_name)
            print(md5_str)
            exist_status = self.redis_cli.sismember('yii',md5_str)
            print(exist_status)
            if exist_status:
                del_status = self.redis_cli.srem('yii',md5_str)
                print('删除状态为: ',del_status)
                mongo_del_status = self.col.delete_one({'_id': fail_data['_id']})
                print('mongo删除状态为: ', mongo_del_status)
            else:
                print('没有包含在redis当中!!')

        #     fail_ele = fail_data['title'] + str(fail_data['date'])
        #     if not fail_ele in success_titles:
        #         print(fail_data['title'])
        #         fail_titles.add(fail_ele)
        #         yield fail_data
        #     else:
        #         print('即将删除数据: {}'.format(str(fail_data)))
        #         data = self.col.delete_one({'_id': fail_data['_id']})
        #         print('删除返回结果为: {}'.format(str(data)))
        # print('待重新请求识别的文件为: ',fail_titles)
        # print('数量为',len(fail_titles))
        # print('本次重新请求 {} 条数据'.format(len(fail_titles)))


        # sql_datas = self.col.find({'title':'近十万例胃黏膜活检样本中幽门螺杆菌检测结果分析'})
        # for sql_data in sql_datas:
        #     # print(sql_data)
        #     yield sql_data
    def get_data(self):
        datas = pd.read_excel('湖北省继续教育网数据_20220922.xlsx')
        print(datas['手机号'].values)
        # for data in datas.iterrows():
        #     print(data['姓名'],data['手机号'])
        return datas['手机号'].values

    def insert(self,phones):
        for phone in phones:
            print(phone)
            status = self.redis_cli.sadd('hbwsrc',str(phone))
            print(status)

    def run(self):
        phones = self.get_data()
        self.insert(phones)


if __name__ == '__main__':

    insert_data = InsertData()
    insert_data.run()