import hashlib
import json
import random
import re
import time
from datetime import datetime

from ..SqlSave.redis_ import RedisCli


class ZwCookie(RedisCli):

    def __init__(self):

        # 在cookie池列表中, 保持20个新鲜的cookie, 以1min为单位, 超过时间将自动删除, 否则持续使用
        super().__init__()
        # self.max_member_num = 30
        # cookie最大失效时长, 默认1小时
        self.max_time_interval = 60
        self.name = 'zw_pdf_cookie_new'

    def insert_cookie(self,key,cookie):

        cookie = json.dumps(cookie,ensure_ascii=False)
        status = self.redis_cli.hset(self.name,key,cookie)
        print('这是更改cookie的状态: {}'.format(status))
        if status == 1:
            print('cookie插入成功!!')
        else:
            print('cookie更新成功!!')

    def have_expire(self,cookie):

        cookie_date = cookie['cookie_date']
        print('cookie 生成时间为: {}'.format(cookie_date))
        now = datetime.now()
        print('当前时间为: {}'.format(cookie_date))
        interval_minutes = int((now - cookie_date).total_seconds() / 60)
        print('时间间隔为: {}'.format(interval_minutes))
        if interval_minutes > self.max_time_interval:
            print('cookie生成已超过2小时未更新, 删除!')
            return 1
        else:
            print('cookie 可正常使用!')
            return 0

    def get_cookie(self):

        # cookie = self.redis_cli.brpop(self.key)
        cookie_keys = self.redis_cli.hkeys(self.name)
        if cookie_keys:
            cookie_key = random.choice(cookie_keys)
            cookie = self.redis_cli.hget(self.name,cookie_key)
            # print('这是所有的cookie: ',cookies)
            # cookie = random.choice(cookies)
            print('取出cookie为: {}'.format(cookie))
            cookie_dic = json.loads(cookie)
            have_expire_status = self.have_expire(cookie_dic)
            if have_expire_status == 0:
                return cookie_dic
            else:
                print('cookie已经过期, 删除掉当前的cookie, 重新选择出最新cookie')
                self.redis_cli.hdel(self.name,cookie_key)
                cookie_dic = self.get_cookie()
                return cookie_dic
            # print(type(cookies))
        else:
            print('redis中存储的cookie为空,等待10分钟, 重新获取cookie!!')
            time.sleep(600)
            self.get_cookie()


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