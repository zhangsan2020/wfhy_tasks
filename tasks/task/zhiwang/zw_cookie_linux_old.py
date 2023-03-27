import hashlib
import random
import re
import time
from ..SqlSave.redis_ import RedisCli


class ZwCookie(RedisCli):

    def __init__(self):

        # 在cookie池列表中, 保持20个新鲜的cookie, 以1min为单位, 超过时间将自动删除, 否则持续使用
        super().__init__()
        self.max_member_num = 30
        # self.max_time_interval = 60
        self.key = 'zw_pdf_cookie'

    def insert_cookie(self,cookie):

        member_num = self.get_length()
        have_exist = self.have_exists(cookie)
        print('当前 redis 数据库中 有 {} 个cookie'.format(member_num))
        if have_exist == 1:
            print('当前cookie已经存在于数据库中,不在插入')
        elif member_num <= self.max_member_num:
            # member_md5 = self.md5_(cookie)
            # cookie['member_md5'] = member_md5
            self.update_cookie(cookie)
            res = self.redis_cli.rpush(self.key,cookie)
            print(res)
            if res:
                print('插入成功')
        else:
            # self.redis_cli.blpop(self.key)
            self.update_cookie(cookie)
            self.redis_cli.rpush(self.key, cookie)
            print('redis 库中cookie超过 {} 个,足够用, 不在加入'.format(member_num))

    def update_cookie(self,new_cookie):

        list_data = self.redis_cli.lrange(self.key, 0, -1)
        # print(data)
        repeat_phone = re.findall('UserName.*?"(1[356789]\d{9})', new_cookie)[0]
        print('开始检测cookie中是否有相同手机号重新登录!')
        print('新cookie中摘取手机号为: {}'.format(repeat_phone))
        for sql_cookie in list_data:
            if repeat_phone in sql_cookie:
                # self.redis_cli.sentinel_remove()
                print('请注意开始删除cookie : {}'.format(sql_cookie))
                self.redis_cli.lrem(self.key,0,sql_cookie)
                print('cookie已经删除')

    def have_exists(self,cookie):
        list_data = self.redis_cli.lrange(self.key,0,-1)

        if cookie in list_data:
            print('当前cookie已经存在与redis list中')
            return 1
        else:
            # print('当前cookie已经存在与redis list中')
            return 0

    def get_cookie(self):

        # cookie = self.redis_cli.brpop(self.key)

        member_num = self.get_length() - 1
        # if member_num >= 5:
        random_index = random.randint(0,member_num)
        print(random_index)
        cookie = self.redis_cli.lindex(self.key,random_index)
        print('这是弹出的cookie: ',cookie)
        time.sleep(random.uniform(0,1))
        return cookie

    # def del_cookie(self):
    #
    #     pass

    def get_length(self):

        member_num = self.redis_cli.llen(self.key)
        return member_num

    # def is_expire(self):
    #
    #     pass

    def md5_(self,item_str):

        print('当前加密字符串为: ',item_str)
        m = hashlib.md5()
        m.update(item_str.encode())
        md5_url = m.hexdigest()
        print(item_str,md5_url)
        return md5_url

if __name__ == '__main__':

    zw_cookie = ZwCookie()
    # ZwCookie.get_cookie()