from task.SqlSave.mongo_store import MongoStore


class WpMongo(MongoStore):

    def find_wp_page_num(self, origin_moudle):

        print('获取mongo中页码数据的基本条件为: {}'.format(origin_moudle))
        page_min_data = [page_num['cur_page'] for page_num in self.col.find(
            {'origin_moudle': origin_moudle}).sort("cur_page").limit(1)]
        page_max_data = [page_num['cur_page'] for page_num in self.col.find(
            {'origin_moudle': origin_moudle}).sort("cur_page", -1).limit(1)]
        # for page_num in page_num_data
        # print('mongo中当前已经存储的页码最小值为: ', page_num_data)

        if page_max_data and page_min_data:
            #     至少有一条数据且能获取到最大最小值
            cur_moudle_sql_total = self.col.count_documents({'origin_module': origin_moudle})
            page_min_data.extend(page_max_data)
            return page_min_data, cur_moudle_sql_total
        else:
            #     all数据库中一条数据都没有, 应该重头倒着抓取
            print('数据库中一条数据也没有,之前从未抓取过,从网站最大页码开始抓取!!')
            return 0
        # if page_num_data:
        #     return page_num_data[0]
        # else:
        #     return 0
        # pass

    def get_module_end_year(self,module_end_year_data):

        reg_data = module_end_year_data + '_over'
        datas = self.col.find({'origin_moudle':reg_data}).sort('spider_date',-1).limit(1)
        for data in datas:
            if data:
                print('找到当前年已经抓取完成的标志, 不再进行数据抓取!!')
                return 'cur_year_over'

    def insert_module_end_year(self,reg_end_year_data):


        end_year_value = reg_end_year_data + '_over'
        res_datas = self.col.find({'origin_moudle':{'$regex':reg_end_year_data}}).sort('spider_date',-1).limit(1)
        for res_data in res_datas:
            print('当前年已经抓取完成,在mongo中添加 module_end_year 标识')
            status = self.col.update_one({'_id':res_data['_id']},{'$set':{'origin_moudle':end_year_value}})
            print(status)
