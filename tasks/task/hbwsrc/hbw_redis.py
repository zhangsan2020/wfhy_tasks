from ..SqlSave.redis_ import RedisCli


class HbRedis(RedisCli):

    def __init__(self):
        super().__init__()

    def md5_(self, item_str):
        return item_str

