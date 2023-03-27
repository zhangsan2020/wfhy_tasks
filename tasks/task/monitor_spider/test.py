import datetime

# print(datetime.strftime('%Y%M%D%H%M%S'))
# print(datetime.now().strftime('%Y%m%d%H%M'))
now = datetime.datetime.now()
# 获取今天零点
zeroToday = now - datetime.timedelta(hours=now.hour, minutes=now.minute, seconds=now.second,microseconds=now.microsecond)
print(zeroToday.strftime('%Y%m%d%H%M'))
# print(datetime.datetime.date())
print(datetime.date.today().strftime('%Y年%m月%d日'))