# coding = utf-8

import logging
import time
class FrameLog:

    def __init__(self,logname,level=logging.INFO):
        #创建日志器
        self.logger = logging.getLogger()
        # 设置日志输出级别
        self.logger.setLevel(level=level)
        # 设置日志路径以及日志文件名
        self.log_time = time.strftime('%Y%m%d_%H%M%S')
        self.log_path = 'F:/wanfang_tasks/tasks/task/log_data/{}/'.format(logname)
        self.log_name = self.log_path + logname + '.log'
        print(self.log_name)
        self.format = logging.Formatter(fmt='%(asctime)s %(filename)s %(lineno)d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %a')
        self.level = level

    def set_filehandler(self):
        # 创建文件处理器
        if not self.logger.handlers:
            self.file_handler = logging.FileHandler(self.log_name, mode='a', encoding='utf-8')
            # 处理器设置日志输出级别
            self.file_handler.setLevel(logging.INFO)
            # 处理器添加格式器
            self.file_handler.setFormatter(self.format)
            # 日志器添加文件处理器
            self.logger.addHandler(self.file_handler)
            # 关闭打开的文件
            self.file_handler.close()


    def get_log(self):
        self.set_filehandler()
        # self.logger.removeHandler(self.file_handler)
        # 返回日志器
        return self.logger


# if __name__ == '__main__':
#     log = FrameLog('test').get_log()
#     log.info('info')
#     log.error('error')
#     log.debug('debug')
#     log.warning('warning')
#     log.critical('严重级别')
