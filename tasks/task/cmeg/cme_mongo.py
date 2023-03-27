from ..SqlSave.mongo_store import MongoStore



class CmeMongo(MongoStore):

    def find_max_page(self,year):

        print('获取mongo中页码数据的基本条件为: {}'.format(year))
        page_num_data = [page_num['cur_page'] for page_num in self.col.find({'year':year}).sort("cur_page",-1).limit(1)]
        # for page_num in page_num_data
        print('mongo中当前已经存储的页码最大值为: ',page_num_data)
        if page_num_data:
            return page_num_data[0]
        else:
            return 0

    def find_base_max_page(self,year):

        print('获取mongo中页码数据的基本条件为: {}'.format(year))
        page_num_data = [page_num['cur_page'] for page_num in self.col.find({'$and':[{'year':year},{'origin_type':'基地项目'}]}).sort("cur_page",-1).limit(1)]
        # for page_num in page_num_data
        print('mongo中当前已经存储的页码最大值为: ',page_num_data)
        if page_num_data:
            return page_num_data[0]
        else:
            return 0