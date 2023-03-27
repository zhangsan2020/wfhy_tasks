# 13901391680
# 010-82195158
# import re
#
# phone = '13901391680'
# # phone = '010-82195158'
#
# if re.findall('1[0-9]{10}',phone):
#     print(re.findall('1[0-9]{10}',phone))
#     print('匹配到了!')

# from datetime import datetime
#
# print(datetime.now().strftime('%Y%m%d%H%m'))


# # 单位
# data_dic['unit'] = tds[1].text
# # 其他负责人
# data_dic['other_leader'] = tds[2].text
# data_dic['other_leader_phone'] = tds[3].text
# data_dic['title'] = tds[4].text
# # 项目负责人
# data_dic['leader'] = tds[5].text
# # 项目负责人手机号
# data_dic['leader_phone'] = tds[6].text
# # 举办期限起止日期
# data_dic['days'] = tds[7].text
# data_dic['place'] = tds[8].text
# # 授予学员学分
# data_dic['score'] = tds[9].text
# # 教学对象
# data_dic['target_stu'] = tds[10].text
# # 拟招生人数
# data_dic['stu_nums'] = tds[11].text
# item.append(tds[5].text)
# item.append(tds[6].text)
# self.mongo_cli.insert(data_dic)


# def isChinese(word):
#     for ch in word:
#         if '\u4e00' <= ch <= '\u9fff':
#             return True
#     return False
#
# print(isChinese('adsfadf'))
# print(isChinese('1'))
import re

data = '13981880412'
print(re.findall('(1[35678]\d{9})[^.\d]', data))
# print(re.findall('(1[35678]\d{9})[^.\d]', '13981880412'))