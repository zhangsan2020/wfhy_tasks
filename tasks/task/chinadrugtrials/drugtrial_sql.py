from ..SqlSave.mongo_store import MongoStore


class DtSql(MongoStore):

    def find_max_sqlpage(self):
        # print(self.col)
        #
        # datas = self.col.find().sort('register_num',-1).limit(1)
        # print(datas)
        # item = {'max_register_num': x['register_num'] for x in datas}
        # return item

        page_data = self.col.find().sort('page_num',-1).limit(1)
        if page_data:
            sql_max_page = {'sql_max_page': x['register_num'] for x in page_data}
            return sql_max_page
        else:
            print('chinadrug 临床网站, mongo中未能获取到最大页码!!')