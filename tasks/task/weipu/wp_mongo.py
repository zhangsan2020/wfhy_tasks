from task.SqlSave.mongo_store import MongoStore


class WpMongo(MongoStore):

    def find_page_num(self, owning_account, origin_moudle):

        print('获取mongo中页码数据的基本条件为: {}__{}'.format(owning_account, origin_moudle))
        page_min_data = [page_num['cur_page'] for page_num in self.col.find(
            {'$and': [{'owning_account': owning_account}, {'origin_moudle': origin_moudle}]}).sort("cur_page").limit(1)]
        page_max_data = [page_num['cur_page'] for page_num in self.col.find(
            {'$and': [{'owning_account': owning_account}, {'origin_moudle': origin_moudle}]}).sort("cur_page", -1).limit(1)]
        # for page_num in page_num_data
        # print('mongo中当前已经存储的页码最小值为: ', page_num_data)

        if page_max_data and page_min_data:
            #     至少有一条数据且能获取到最大最小值
            page_min_data.extend(page_max_data)
            return page_min_data
        else:
            #     all数据库中一条数据都没有, 应该重头倒着抓取
            print('数据库中一条数据也没有,之前从未抓取过,从网站最大页码开始抓取!!')
            return 0
        # if page_num_data:
        #     return page_num_data[0]
        # else:
        #     return 0
        # pass
