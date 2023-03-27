
from crontab import CronTab

# 方法一

# # 创建cron访问
# cron = CronTab(user='root')
#
# # 增加新作业
# job = cron.new(command='echo hello_world')
#
# # 每一分钟执行一次
# job.minute.every(1)
#
# # 写入作业
# cron.write()

# 方法二
# with CronTab(user='hello') as cron:
#
#     # job = cron.new(command='/usr/bin/python3 /home/zl/wfhy/work/tasks/run_send_message.py')
#     # job = cron.new(command='C:/Users/hello/AppData/Local/Microsoft/WindowsApps/python3.exe C:/Users/hello/Desktop/linux_tasks/tasks/run_send_message.py')
#
#     job.minute.every(1)

# print('cron.write() was just executed')

mem_cron = CronTab(tab="*/1 * * * * C:/Users/hello/AppData/Local/Programs/Python/Python39/python39.exe F:/wanfang_tasks/tasks/run_send_message.py")

