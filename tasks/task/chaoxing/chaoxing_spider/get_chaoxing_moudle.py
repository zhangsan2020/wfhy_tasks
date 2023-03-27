import json
import os
from lxml import etree


def get_moudles():
    keywords = {}
    qikans = {}
    dir_path = 'F:/wanfang_tasks/tasks/task/chaoxing/chaoxing_moudle'
    for files in os.listdir(dir_path):
        print('当前文件是: {}'.format(files))
        if 'html' in files:
            with open('{}/{}'.format(dir_path, files), 'r', encoding='utf-8') as f:
                html_data = f.read()
            html = etree.HTML(html_data)
            keywords_div = html.xpath('//div[@name="keywords"]')
            # print(keywords_div)
            # print(len(keywords_div))

            for div in keywords_div:
                # print(div)
                name = div.xpath('.//font/@title')[0].strip()
                # print(name)
                value = div.xpath('./@value')[0].strip()
                keywords[name] = value
            # print(keywords)

            qikans_div = html.xpath('//div[@name="mags"]')
            # print(qikans_div)
            # print(len(qikans_div))

            for div in qikans_div:
                # print(div)
                name = div.xpath('.//font/@title')[0].strip()
                # print(name)
                value = div.xpath('./@value')[0].strip()
                qikans[name] = value
            # print(qikans)

    print('keywords最终长度: ', len(keywords))
    print('keywords最终结果: ', keywords)
    print('qiankans最终长度: ', len(qikans))
    print('keywords最终结果: ', qikans)
    return keywords, qikans


# tasks = []



# def get_tasks():
#     keywords, qikans = get_moudles()
#     print(keywords)
#     print(qikans)
#     # for year in range(2022, 2014, -1):
#     for second_name, second_value in keywords.items():
#         for third_name, third_value in qikans.items():
#             task_format = {
#                 "platform": "机构",
#                 "keywords": "医院",
#                 "max_year": 2022,
#                 "min_year": 2014,
#                 "page_size": 50,
#                 "have_start": 0,
#                 "have_end": 0,
#                 "max_page": 15,
#                 "is_running": 0,
#                 "level": 1,
#                 "cur_year": 2022,
#                 "spider_at": "win",
#                 "owning_account": "6849_超星1",
#                 "origin_moudle": "机构_医院_2022_疗效_中国保健营养"
#             }
#             task_format['second_name'] = second_name
#             task_format['second_value'] = second_value
#             task_format['third_name'] = third_name
#             task_format['third_value'] = third_value
#             task_format['origin_moudle'] = "{}_{}_{}_{}_{}".format(task_format['platform'], task_format['keywords'],
#                                                                    task_format['cur_year'],second_name,third_name)
#             print('这是task_format: ',task_format)
#             tasks.append(task_format)
#             print('这是tasks:', tasks)
#         # break
#     # print(tasks)
#     with open('./chaoxing_tasks.json', 'w', encoding='utf-8') as f:
#         f.write(json.dumps(tasks, ensure_ascii=False))
#         f.close()
#
#
# get_tasks()
