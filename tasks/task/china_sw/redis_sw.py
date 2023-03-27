import hashlib
from task.SqlSave.redis_ import RedisCli


class SwRedis(RedisCli):

    # def __init__(self):
    #     super().__init__()

    def set_item(self,key,item_str):
        '''
        放入集合进行去重
        :param name:
        :param item:
        :return:
        '''
        md5_data = self.md5_(item_str)
        flag = self.redis_cli.sadd(key,md5_data)
        if flag == 1:
            print('插入resdis集合成功!!')
            return 1
        elif flag == 0:
            print('该数据已经抓取过且已经存入数据库,不再抓取')
            return 0
        else:
            print('插入集合存在其它问题')

    def md5_(self,item_str):

        # print('当前加密字符串为: ',item_str)
        m = hashlib.md5()
        m.update(item_str.encode())
        md5_data = m.hexdigest()
        print(item_str,md5_data)
        return md5_data