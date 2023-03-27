# # # -*- coding:utf-8 -*-
# # import re
# #
# # from jsonpath import jsonpath
# # # import json
# # # data = '[{"key":"SCDB","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"篇名","Value":"TI$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"作者","Value":"AU$=|"},{"ColName":"","Text":"第一作者","Value":"FI$=|"},{"ColName":"","Text":"通讯作者","Value":"RP$%=|"},{"ColName":"","Text":"作者单位","Value":"AF$%"},{"ColName":"","Text":"基金","Value":"FU$%|"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"小标题","Value":"CO$%=|"},{"ColName":"","Text":"参考文献","Value":"RF$%=|"},{"ColName":"","Text":"分类号","Value":"CLC$=|??"},{"ColName":"","Text":"文献来源","Value":"LY$%=|"},{"ColName":"","Text":"DOI","Value":"DOI$=|?"}]}]},{"key":"CJFQ","Value":[{"ColName":"篇章信息","FieldList":[{"ColName":"篇章信息","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"篇章信息","Text":"篇名","Value":"TI$%=|"},{"ColName":"篇章信息","Text":"关键词","Value":"KY$=|"},{"ColName":"篇章信息","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"小标题","Value":"CO$%=|"},{"ColName":"篇章信息","Text":"全文","Value":"FT$%=|"},{"ColName":"篇章信息","Text":"参考文献","Value":"RF$%=|"},{"ColName":"篇章信息","Text":"基金","Value":"FU$%|"},{"ColName":"篇章信息","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"篇章信息","Text":"DOI","Value":"DOI$=|?"}]},{"ColName":"作者/机构","FieldList":[{"ColName":"作者/机构","Text":"作者","Value":"AU$=|"},{"ColName":"作者/机构","Text":"第一作者","Value":"FI$=|"},{"ColName":"作者/机构","Text":"通讯作者","Value":"RP$=|"},{"ColName":"作者/机构","Text":"作者单位","Value":"AF$%"},{"ColName":"作者/机构","Text":"第一单位","Value":"FAF$%"}]},{"ColName":"期刊信息","FieldList":[{"ColName":"期刊信息","Text":"期刊名称","Value":"LY$%=|"},{"ColName":"期刊信息","Text":"ISSN","Value":"SN$=|??"},{"ColName":"期刊信息","Text":"CN","Value":"CN$=|??"},{"ColName":"期刊信息","Text":"栏目信息","Value":"QKLM$%=|??"}]}]},{"key":"CCND","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"题名","Value":"TI$%=|"},{"ColName":"","Text":"小标题","Value":"CO$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"作者","Value":"AU$=|"},{"ColName":"","Text":"第一作者","Value":"FI$=|"},{"ColName":"","Text":"作者单位","Value":"AF$=|"},{"ColName":"","Text":"报纸名称","Value":"LY$=|"},{"ColName":"","Text":"国内统一刊号","Value":"CN$=|??"},{"ColName":"","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"","Text":"DOI","Value":"DOI$=|?"}]}]},{"key":"CIPD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"篇名","Value":"TI$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"作者","Value":"AU$=|"},{"ColName":"","Text":"第一作者","Value":"FI$=|"},{"ColName":"","Text":"单位","Value":"AF$%"},{"ColName":"","Text":"会议名称","Value":"CV$%=|"},{"ColName":"","Text":"主办单位","Value":"HAF$%=|"},{"ColName":"","Text":"基金","Value":"FU$%|"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"小标题","Value":"CO$%=|"},{"ColName":"","Text":"论文集名称","Value":"LY$%=|"},{"ColName":"","Text":"参考文献","Value":"RF$%=|"},{"ColName":"","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"","Text":"DOI","Value":"DOI$=|?"}]}]},{"key":"CDMD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"题名","Value":"TI$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"作者","Value":"AU$=|"},{"ColName":"","Text":"作者单位","Value":"AF$=|"},{"ColName":"","Text":"导师","Value":"TU$=|"},{"ColName":"","Text":"第一导师","Value":"FTU$=|"},{"ColName":"","Text":"学位授予单位","Value":"LY$%|"},{"ColName":"","Text":"基金","Value":"FU$%|"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"目录","Value":"CO$%=|"},{"ColName":"","Text":"参考文献","Value":"RF$%=|"},{"ColName":"","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"","Text":"学科专业名称","Value":"XF$%|"},{"ColName":"","Text":"DOI","Value":"DOI$=|?"}]}]},{"key":"CYFD","Value":[{"ColName":"条目信息","FieldList":[{"ColName":"条目信息","Text":"主题","Value":"SU$%=|"},{"ColName":"条目信息","Text":"题名","Value":"TI$%=|"},{"ColName":"条目信息","Text":"正文","Value":"FT"},{"ColName":"","Text":"DOI","Value":"DOI$=|?"}]},{"ColName":"编者","FieldList":[{"ColName":"编者","Text":"主编","Value":"ZB"},{"ColName":"编者","Text":"主编单位","Value":"DF"},{"ColName":"编者","Text":"条目作者","Value":"AU"},{"ColName":"编者","Text":"作者单位","Value":"AF$%=|"}]},{"ColName":"年鉴信息","FieldList":[{"ColName":"年鉴信息","Text":"年鉴名称","Value":"LY$%=|"},{"ColName":"年鉴信息","Text":"ISSN","Value":"IS"},{"ColName":"年鉴信息","Text":"ISBN","Value":"IB"},{"ColName":"年鉴信息","Text":"CN","Value":"CN"},{"ColName":"年鉴信息","Text":"卷","Value":"JA"},{"ColName":"年鉴信息","Text":"出版者","Value":"PU$%=|"},{"ColName":"年鉴信息","Text":"出版日期","Value":"PD"}]}]},{"key":"WWBD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"标题","Value":"TI$%=|"},{"ColName":"","Text":"作者","Value":"AU"},{"ColName":"","Text":"关键词","Value":"KY"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"DOI","Value":"DOI"},{"ColName":"","Text":"单位","Value":"AF"},{"ColName":"","Text":"出版社","Value":"LY"}]}]},{"key":"SCOD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"专利名称","Value":"TI$%=|"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"申请号","Value":"SQH$=|??"},{"ColName":"","Text":"公开号","Value":"GKH$=|??"},{"ColName":"","Text":"分类号","Value":"CLZ$=|??"},{"ColName":"","Text":"主分类号","Value":"CLC$=|??"},{"ColName":"","Text":"申请人","Value":"AF$=|"},{"ColName":"","Text":"发明人","Value":"AU$=|"},{"ColName":"","Text":"代理人","Value":"DLR$=|"},{"ColName":"","Text":"同族专利项","Value":"TSC$%=|"},{"ColName":"","Text":"优先权","Value":"YXQ$%=|"}]}]},{"key":"CISD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"标准名称","Value":"TI$%=|"},{"ColName":"","Text":"标准号","Value":"BZH$=|??"},{"ColName":"","Text":"关键词","Value":"KY"},{"ColName":"","Text":"摘要","Value":"AB$%="},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"起草人","Value":"AU$%|"},{"ColName":"","Text":"起草单位","Value":"AF$%="},{"ColName":"","Text":"发布单位","Value":"DF$%"},{"ColName":"","Text":"出版单位","Value":"SDF$%"},{"ColName":"","Text":"中国标准分类号","Value":"CLC$=|??"},{"ColName":"","Text":"国际标准分类号","Value":"CLZ$=|??"}]}]},{"key":"SNAD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"成果名称","Value":"TI$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"成果简介","Value":"AB$%=|"},{"ColName":"","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"","Text":"学科分类号","Value":"CLZ$=|??"},{"ColName":"","Text":"成果完成人","Value":"AU$=|"},{"ColName":"","Text":"第一完成单位","Value":"AF$%=|"},{"ColName":"","Text":"单位所在省市","Value":"SZS$=|?"},{"ColName":"","Text":"合作完成单位","Value":"SDF$%=|"}]}]},{"key":"CCJD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"","Text":"篇名","Value":"TI$%=|"},{"ColName":"","Text":"关键词","Value":"KY$=|"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"作者","Value":"AU$=|"},{"ColName":"","Text":"第一作者","Value":"FI$=|"},{"ColName":"","Text":"作者单位","Value":"AF$%|"},{"ColName":"","Text":"参考文献","Value":"RF$%=|"},{"ColName":"","Text":"辑刊名称","Value":"LY$%=|"},{"ColName":"","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"","Text":"基金","Value":"FU$%|"}]}]},{"key":"BDZK","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"标题","Value":"TI$%=|"},{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"作者","Value":"AU$=|"},{"ColName":"","Text":"关键词","Value":"KY"},{"ColName":"","Text":"摘要","Value":"AB$%=|"},{"ColName":"","Text":"DOI","Value":"DOI$=|?"},{"ColName":"","Text":"单位","Value":"AF$%"},{"ColName":"","Text":"出版社","Value":"LY"},{"ColName":"","Text":"目录","Value":"CO$%=|"},{"ColName":"","Text":"基金","Value":"FU$%|"},{"ColName":"","Text":"参考文献","Value":"RF$%=|"},{"ColName":"","Text":"分类号","Value":"CLC$=|??"}]}]},{"key":"GXDB","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"全文","Value":"FT$%=|"},{"ColName":"","Text":"书名","Value":"TI$%=|"},{"ColName":"","Text":"著者","Value":"AU"},{"ColName":"","Text":"卷名","Value":"TY"}]}]},{"key":"CJFN","Value":[{"ColName":"篇章信息","FieldList":[{"ColName":"篇章信息","Text":"主题","Value":"SU$%=|"},{"ColName":"","Text":"篇关摘","Value":"TKA$%=|"},{"ColName":"篇章信息","Text":"篇名","Value":"TI$%=|"},{"ColName":"篇章信息","Text":"关键词","Value":"KY$=|"},{"ColName":"篇章信息","Text":"摘要","Value":"AB$%=|"},{"ColName":"篇章信息","Text":"全文","Value":"FT$%=|"},{"ColName":"篇章信息","Text":"参考文献","Value":"RF$%=|"},{"ColName":"篇章信息","Text":"基金","Value":"FU$%|"},{"ColName":"篇章信息","Text":"中图分类号","Value":"CLC$=|??"},{"ColName":"篇章信息","Text":"DOI","Value":"DOI$=|?"}]},{"ColName":"作者/机构","FieldList":[{"ColName":"作者/机构","Text":"作者","Value":"AU$=|"},{"ColName":"作者/机构","Text":"第一作者","Value":"FI$=|"},{"ColName":"作者/机构","Text":"通讯作者","Value":"RP$=|"},{"ColName":"作者/机构","Text":"作者单位","Value":"AF$%"},{"ColName":"作者/机构","Text":"第一单位","Value":"FAF$%"}]},{"ColName":"期刊信息","FieldList":[{"ColName":"期刊信息","Text":"期刊名称","Value":"LY$%=|"},{"ColName":"期刊信息","Text":"ISSN","Value":"SN$=|??"},{"ColName":"期刊信息","Text":"CN","Value":"CN$=|??"},{"ColName":"期刊信息","Text":"栏目信息","Value":"QKLM$%=|??"}]}]},{"key":"CRLD","Value":[{"ColName":"","FieldList":[{"ColName":"","Text":"被引主题","Value":"SU$%=|"},{"ColName":"","Text":"被引题名","Value":"TI$%=|"},{"ColName":"","Text":"被引关键词","Value":"KY$=|"},{"ColName":"","Text":"被引摘要","Value":"AB$%=|"},{"ColName":"","Text":"被引作者","Value":"AU$=|"},{"ColName":"","Text":"被引单位","Value":"AF"},{"ColName":"","Text":"被引文献来源","Value":"LY"}]}]}]'
# # #
# # # def search_first_match(all_data,search_data):
# # #     jsondatas = json.loads(all_data)
# # #     key_datas = {}
# # #     for jsondata in jsondatas:
# # #         flag_data = jsonpath(jsondata, '$.Value[*].FieldList[?(@.Text=="{}")]'.format(search_data))
# # #         if flag_data:
# # #             search_table = jsonpath(jsondata, '$.key')[0]
# # #             search_key = jsonpath(flag_data,'$[*].Text')[0]
# # #             search_value = re.findall('\w+',jsonpath(flag_data, '$[*].Value')[0])[0]
# # #             key_datas[search_table] = {search_key:search_value}
# # #     print(key_datas)
# # #
# # # search_first_match(data,'作者单位')
# # # # {'SCDB': {'作者单位': 'AF'}, 'CJFQ': {'作者单位': 'AF'}, 'CCND': {'作者单位': 'AF'}, 'CDMD': {'作者单位': 'AF'}, 'CYFD': {'作者单位': 'AF'}, 'CCJD': {'作者单位': 'AF'}, 'CJFN': {'作者单位': 'AF'}}
# #
# # # 年
# # # "Key":"2021","Title":"2021","Logic":2,"Name":"年","Operate":"","Value":"2021"
# # # 学科
# # # "Key":"E066?","Title":"外科学","Logic":2,"Name":"专题子栏目代码","Operate":"","Value":"E066?"
# # # 研究层次
# # # "Key":"131","Title":"技术研究-临床医学试验研究","Logic":2,"Name":"人工标识码","Operate":"","Value":"131",
# # # {'years':[],'subjects':[{},{}],'study_level':[{},{}]}
# #
# # from lxml import etree
# # group_datas = {'subjects':{'info':{}},'study_level':{'info':{}}}
# # data = open('./cnki_resulturl.html','r',encoding='utf-8').read()
# # html = etree.HTML(data)
# # group_datas['years'] = html.xpath('//dd[@tit="发表年度"]//li/input/@text')
# # sub_field = html.xpath('//dd[@tit="学科"]/@field')[0]
# # group_datas['subjects']['field'] = sub_field
# # lis_sub = html.xpath('//dd[@tit="学科"]//li')
# # # print(lis_sub)
# # for li in lis_sub:
# #     name = li.xpath('./input/@text')[0]
# #     group_datas['subjects']['info'][name] = li.xpath('./input/@value')[0]
# #     # print(name)
# # study_field = html.xpath('//dd[@tit="研究层次"]/@field')[0]
# # group_datas['study_level']['field'] = study_field
# # lis_study = html.xpath('//dd[@tit="研究层次"]//li')
# # # print(lis_study)
# # for study in lis_study:
# #     name = study.xpath('./input/@text')[0]
# #     group_datas['study_level']['info'][name] = study.xpath('./input/@value')[0]
# # print(group_datas)
# # # a = {'QueryJson': '{"Platform":"","DBCode":"CJFQ","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' +
# # #                          self.searchinfo['model'] + '","Name":"' + self.searchinfo['model_match_data'] + '","Value":"' + self.searchinfo['keywords'] + '","Operate":""}],"ChildItems":[]}]}}'}
# #
# #
# # # 年
# # # "Key":"2021","Title":"2021","Logic":2,"Name":"年","Operate":"","Value":"2021"
# # # 学科
# # # "Key":"E066?","Title":"外科学","Logic":2,"Name":"专题子栏目代码","Operate":"","Value":"E066?"
# # # 研究层次
# # # "Key":"131","Title":"技术研究-临床医学试验研究","Logic":2,"Name":"人工标识码","Operate":"","Value":"131",
# # # {'years':[],'subjects':[{},{}],'study_level':[{},{}]}
# # # year = '2021'
# # # choice_moudle = {}
# # # sub_info = []
# # # stu_info = []
# # b = '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"'+ self.searchinfo['model'] +'","Name":"' + self.searchinfo['model_match_data'] + '","Value":"' + self.searchinfo['keywords'] + '","Operate":"%"}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"'+ sub_info[1] +'?","Title":"' + sub_info[0] + '","Logic":2,"Name":"' + choice_moudle['subjects']['field'] + '","Operate":"","Value":"' + sub_info[1] + '?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"' + year + '","Title":"' + year + '","Logic":2,"Name":"年","Operate":"","Value":"' + year + '","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"4","Title":"","Logic":1,"Items":[{"Key":"' + stu_info[1] + '","Title":"' + stu_info[0] + '","Logic":2,"Name":"' + choice_moudle['study_level']['field'] + '","Operate":"","Value":"' + stu_info[1] + '","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]}}'
# # #
# # #
# # #
# #
# #
# # a = 'queryJson: {"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CDMD,CIPD,CCND,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"作者单位","Name":"AF","Value":"医院","Operate":"%"}],"ChildItems":[]},{"Key":"SCDBGroup","Title":"","Logic":1,"Items":[],"ChildItems":[{"Key":"2","Title":"","Logic":1,"Items":[{"Key":"E057?","Title":"中药学","Logic":2,"Name":"专题子栏目代码","Operate":"","Value":"E057?","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"3","Title":"","Logic":1,"Items":[{"Key":"2022","Title":"2022","Logic":2,"Name":"年","Operate":"","Value":"2022","ExtendType":0,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]},{"Key":"4","Title":"","Logic":1,"Items":[{"Key":"12","Title":"应用基础研究","Logic":2,"Name":"人工标识码","Operate":"","Value":"12","ExtendType":14,"ExtendValue":"","Value2":"","BlurType":""}],"ChildItems":[]}]}]}}'
# # import hashlib
# # import re
# #
# # # name = '{}_{}.pdf'.format(item['title'].replace('/', '_'), item['date'].replace(' ', '&'))
# # # print('name等于: ',name)
# # # file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", name)
# # # item_str = '手术史对化疗所致恶心呕吐影响的病例对照研究_2022-10-12.pdf'
# # # def request_dumplite(item_str):
# # #     m = hashlib.md5()
# # #     m.update(item_str.encode())
# # #     md5_url = m.hexdigest()
# # #     print(item_str,md5_url)
# # #     return md5_url
# # # data = request_dumplite(item_str)
# # # print(data)
# #
# # # print(round(5.123, 2))
# #
# # # a = ['he','adsf','eer','eee']
# # # print([('主要主题', x) for x in a])
# # import time
# #
# # # group_datas = {'subjects': {'info': {'临床医学': 'E060', '外科学': 'E066', '肿瘤学': 'E072', '中医学': 'E056', '心血管系统疾病': 'E062', '内分泌腺及全身性疾病': 'E065', '儿科学': 'E069', '神经病学': 'E070', '妇产科学': 'E068', '眼科与耳鼻咽喉科': 'E073', '泌尿科学': 'E067', '消化系统疾病': 'E064', '医药卫生方针政策与法律法规研究': 'E053', '中药学': 'E057', '急救医学': 'E077', '药学': 'E079', '感染性疾病及传染病': 'E061', '口腔科学': 'E074', '呼吸系统疾病': 'E063', '预防医学与卫生学': 'E055'}, 'field': '专题子栏目代码'}, 'topics': [('主要主题', '临床观察'), ('主要主题', '临床分析'), ('主要主题', '临床研究'), ('主要主题', '临床意义'), ('主要主题', '糖尿病'), ('主要主题', '护理体会'), ('主要主题', '疗效分析'), ('主要主题', '效果观察'), ('主要主题', '高血压'), ('主要主题', '相关性研究'), ('主要主题', '冠心病'), ('主要主题', '中西医结合治疗'), ('主要主题', '手术治疗'), ('主要主题', '临床疗效观察'), ('主要主题', '糖尿病患者'), ('主要主题', '护理干预'), ('主要主题', '应用价值'), ('主要主题', '腹腔镜'), ('主要主题', '乳腺癌'), ('主要主题', '临床效果'), ('次要标题', '统计学意义'), ('次要标题', '治疗组'), ('次要标题', '实验组'), ('次要标题', '临床效果'), ('次要标题', '总有效率'), ('次要标题', '老年人'), ('次要标题', '治疗前后'), ('次要标题', '模型组'), ('次要标题', '不良反应'), ('次要标题', '手术治疗'), ('次要标题', '磁共振成像'), ('次要标题', '并发症'), ('次要标题', '治疗效果'), ('次要标题', '阳性率'), ('次要标题', '护理人员'), ('次要标题', '比较差异'), ('次要标题', '危险因素'), ('次要标题', '发病率'), ('次要标题', '临床表现'), ('次要标题', '临床疗效')]}
# # #
# # # years = ['2022', '2021', '2020', '2019', '2018', '2017']
# # # i = 1
# # # for year in years:
# # #     for subject_info in group_datas['subjects']['info'].items():
# # #         for i,topic_data in enumerate(group_datas['topics']):
# # #             for page_num in range(299, 300):
# # #                 print(page_num)
# # #                 print('当前遍历是, 第{}次'.format(i))
# # #                 i += 1
# # #
# # #             group_datas['topics'] = [2,23,4,6]
# # #             time.sleep(1)
# # #         exit()
# #
# #
# #
# # # a = [23,56,32,56,76,33]
# # # b = 3
# # # print(a[b:])
# #
# # # a = {'info':{
# # #     'name':'张三',
# # #     'age':25
# # # }}
# # # # print(list(a.keys())[0])
# # # print(a.items())
# #
# #
# #
# # import requests
# # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-US; rv:1.0.1) Gecko/20021104 Chimera/0.6'}
# # url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2509&k=&num=50&page=1'
# # resp = requests.get(url,headers=headers)
# # print(resp.status_code)
# # print(resp.text)
# import os
# from datetime import datetime
#
# start_date = datetime.strptime('202211231000','%Y%m%d%H%M')
# spider_date = datetime.now()
# print(start_date,spider_date)
# print(dir(spider_date-start_date))
# print((spider_date-start_date).total_seconds())
# interval_seconds = (spider_date-start_date).total_seconds()/60
# if interval_seconds > 300:
#     print('cookie生成已超过5小时未更新, 删除!')
# else:
#     print('cookie 可正常使用!')
#
# print(os.path.basename(__file__))
#
#
#
#
#
#
#
#
#
#
#


# import requests
#
# headers = {
#     'authority': 'www.xyhos.com',
#     'method': 'GET',
#     'path': '/list-109.html?page=4',
#     'scheme': 'https',
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'accept-encoding': 'gzip, deflate',
#     'accept-language': 'zh-CN,zh;q=0.9',
#     'cache-control': 'max-age=0',
#     'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'document',
#     'sec-fetch-mode': 'navigate',
#     'sec-fetch-site': 'none',
#     'sec-fetch-user': '?1',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
# }
# # https://www.xyhos.com/list-109.html?page=3
# res = requests.get('https://www.xyhos.com/list-109.html?page=3',headers=headers)
# print(res.text)








import requests
import ddddocr
import requests
import time
username = '15210559392'
password = 'mengyao2016'
session = requests.Session()
# url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111308977757779163387_1664344204467&userName=1029025432%40qq.com&pwd=asdfasdf&isAutoLogin=true&p=2&_=1664344204476'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
def login():

    img_retry = 1
    imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
    res = session.get(imgcode_url,headers=headers)
    with open('./code.jpg','wb') as f:
        f.write(res.content)
    code_str = get_checkcode('./code.jpg')
    print('识别出验证码为: ',code_str)

def get_checkcode(img):
    ocr = ddddocr.DdddOcr(old=True)
    # 第一个验证截图保存：verification_code_1.png
    with open(img, 'rb') as f:
        image = f.read()
    res = ocr.classification(image)
    return res


login()








