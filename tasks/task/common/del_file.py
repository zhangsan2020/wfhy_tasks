import datetime
import os
import time


# def check_path():
#     full_path = os.path.join(settings.MEDIA_ROOT, "file")
#     if not os.path.exists(full_path):
#        os.makedirs(full_path)
#     return full_path

def delete_old_file(date_data):

    # full_path = check_path()
    sizes = []
    zw_path_e = 'E:/zhiwang_pdfs/'
    zw_path_f = 'F:/zhiwang_pdfs/'
    wp_path_e = 'E:/weipu_pdfs/'
    wp_path_f = 'F:/weipu_pdfs/'
    yixuehui_path_e = 'E:/yixuehui_pdfs/'
    yixuehui_path_f = 'F:/yixuehui_pdfs/'
    chinasw_path_e = 'E:/chinasw_pdfs/'
    chinasw_path_f = 'F:/chinasw_pdfs/'
    full_paths = [zw_path_e,zw_path_f,wp_path_e,wp_path_f,yixuehui_path_e,yixuehui_path_f,chinasw_path_e,chinasw_path_f]
    for full_path in full_paths:
        if os.path.exists(full_path):
            print('当前删除的路径地址为: {}'.format(full_path))
            time.sleep(3)
            print('开始删除文件!!')
            time.sleep(2)
            for file in os.listdir(full_path):
               file_path = os.path.join(full_path, file)
               # print(os.path.getsize(file_path))
               # size = os.path.getsize(file_path)

               # 根据文件大小删除数据
            #    if int(size) > 51200:
            #        sizes.append(size)
            #    else:
            #        print(file_path)
            #        os.remove(file_path)
            # print(sorted(sizes)[:10])
            # print('最小值文件为: {}, 大小为:{}'.format(file_path,min(sizes)))
               # print(file_path)
               t = os.path.getmtime(file_path)
               datetime_t = datetime.datetime.fromtimestamp(t)
               print('datetime_t: ',datetime_t)
               datetime_t_str = datetime_t.strftime('%Y-%m-%d %H:%M:%S')
               now_time = datetime.datetime.now()
               now_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
               d1 = datetime.datetime.strptime(datetime_t_str, '%Y-%m-%d %H:%M:%S')
               d2 = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
               # 间隔天数
               # print(dir((d2 - d1)))
               day_num = (d2 - d1).total_seconds()
               if day_num >= date_data:
                   print('距离当前时间超过{}秒, 删除该文件'.format(date_data))
                   os.remove(file_path)
               else:
                   print('{}秒范围内, 不变'.format(date_data))
        else:
            print('该路径地址不存在, 跳过!!')

date_data = 100
delete_old_file(date_data)