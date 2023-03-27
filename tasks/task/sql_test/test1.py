import pymongo
import re
class Mongo_():

    def __init__(self):

        self.mongo_cli = pymongo.MongoClient('127.0.0.1',27017)
        # self.db = self.mongo_cli.
        self.db = self.mongo_cli['wfhy']


    def handler(self):

        datas = self.db.chictr.find({'url_id':None})
        print(datas)
        for data in datas:
            print(data)
            print(data['detail_url'])
            detail_url = data['detail_url']
            if re.search('\d+',detail_url).group():
                num = int(re.search('\d+',detail_url).group())
                print(num)
                self.db.chictr.update_many({'detail_url':detail_url},{'$set':{'url_id':num}})
                # print(num)


if __name__ == '__main__':

    mg = Mongo_()
    mg.handler()