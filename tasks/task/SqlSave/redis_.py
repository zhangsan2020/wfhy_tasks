import redis
from ..common.common_data import redis_main_info
import hashlib

class RedisCli():

    def __init__(self):

        # self.redis_cli = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
        self.redis_cli = redis.Redis(host= redis_main_info['host'], password=redis_main_info['password'], port=redis_main_info['port'], decode_responses=True,health_check_interval=320)
        #  造一个链接池，最多能放100个连接
        #  以模块导入，天然单例
        # from POOL import CONN_POOL  # 绝对导入
        #
        # pool = redis.ConnectionPool(host='127.0.0.1', port=6379, max_connections=100)
        #
        # # 只要执行这句话，就从池中拿出一个连接
        #
        # conn = redis.Redis(connection_pool=pool)
    def set_item(self, key, phone):
        '''
        放入集合进行去重
        :param name:
        :param item:
        :return:
        '''
        flag = self.redis_cli.sadd(key, phone)
        if flag == 1:
            print('插入resdis集合成功!!')
            return 1
        elif flag == 0:
            print('该数据已经抓取过且已经存入数据库, 不在放入到commit表中!')
            return 0
        else:
            print('插入集合存在其它问题')

    def insert_phone(self, key, phone):
        '''
        放入集合进行去重
        :param name:
        :param item:
        :return:
        '''
        flag = self.redis_cli.sadd(key, phone)
        if flag == 1:
            print('插入 all_phones_pdf 集合成功!!')
            return 1
        elif flag == 0:
            print('当前手机号已经存在, 不再加入 all_phones_pdf 集合中!!')
            return 0
        else:
            print('插入 all_phones_pdf 集合存在其它问题')
    # def set_item(self,key,item_str):
    #     '''
    #     放入集合进行去重
    #     :param name:
    #     :param item:
    #     :return:
    #     '''
    #     md5_url = self.md5_(item_str)
    #     flag = self.redis_cli.sadd(key,md5_url)
    #     if flag == 1:
    #         print('插入resdis集合成功!!')
    #         return 1
    #     elif flag == 0:
    #         print('该数据已经抓取过且已经存入数据库,不再抓取')
    #         return 0
    #     else:
    #         print('插入集合存在其它问题')

    # def md5_(self,item_str):
    #
    #     print('当前加密字符串为: ',item_str)
    #     m = hashlib.md5()
    #     m.update(item_str.encode())
    #     md5_url = m.hexdigest()
    #     print(item_str,md5_url)
    #     return md5_url
