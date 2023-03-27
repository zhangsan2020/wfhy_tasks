from pymongo import MongoClient
mongo = MongoClient('mongodb://127.0.0.1:27017')
db = mongo['wfhy']


def getnextid():

    ret = db.china_.find_one_and_update({"_id": 'productid'}, {"$inc": {"sequence_value": 1}}, safe=True, new=True)

    nextid = ret["sequence_value"]

    return nextid
