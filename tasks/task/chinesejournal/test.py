# import requests
# data = {"group": "rpc-test",
#         "action": "clientTime",
#         }
# res = requests.get("http://127.0.0.1:5620/business-demo/invoke",params=data )
# print(res.text)
import re
#
# data = "var vpn_return;eval(vpn_rewrite_js((function () { showdown('7108381222','9YXLwU4VPo6YUZ3IncEGUqH%2fysl%2blPbD%2bW0EZBC6w211bYUOqbXYdw%3d%3d') }).toString().slice(14, -2), 2));return vpn_return;"
# article_data = re.findall("showdown\('(\d+)','(.*?)'\)",data)
# print(article_data)

# file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", '《手术安全核查制度》实施10年,我们还有哪些问题?'+'.pdf')
# print(file_name)

# from urllib import parse
# text = 'AtZeRpSg6jxonUUrhCd89Qb%2ftpg6ze4bSKjIkPQtrqA%3d'
#进行url编码，但是这步会将&与=一起转码，一般把普通链接转换成浏览器可以识别的url链接
#有时候可能需要编码两次，有的操作会自动转码，把链接转两次后再操作，得到就是原版转一次的链接。
# text2 = parse.quote(text)
# print(text2)
# #进行url解码，但是不会将拼接形式转换为字典形式
# text1 = parse.unquote(text)
#
# print(text1)


def person(name, age, **kw):
    print('name:', name, 'age:', age, 'other:', kw)
     # **函数person除了必选参数name和age外，还接受关键字参数kw。在调用该函数时，可以只传入必选参数**：
person('Michael', 30)
person('Bob', 35, city='Beijing')
person('Adam', 45, gender='M', job=12)