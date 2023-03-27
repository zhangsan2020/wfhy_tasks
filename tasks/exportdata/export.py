import pymongo

mongo_cli = pymongo.MongoClient(host='127.0.0.1',port=27017)
db = mongo_cli['wfhy_commit']
col = db['chictr_commit_copy1']
datas = col.find({'commit_status':'未提交'})
for data in datas:
    print(data)