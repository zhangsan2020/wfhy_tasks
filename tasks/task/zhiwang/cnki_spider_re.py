import os
import random
import re
from datetime import datetime
from urllib.parse import urljoin
from lxml import etree
import ddddocr
import requests
import time
from requests.adapters import HTTPAdapter
from .zw_common import user_info, headers_list
from .cur_identify import CurIdentify
from ..SqlSave.mongo_store import MongoStore
from .redis_zw import ZwRedis
from ..common.log import FrameLog
from .re_down_pdf import ReDownPdf

class ZwReDown():

    def __init__(self):

        self.headers_init = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.list_url = 'https://kns.cnki.net/kns8/Brief/GetGridTableHtml'
        self.userinfo = user_info
        self.headers_list = headers_list
        self.searchinfo = {'title': '作者单位', 'keywords': '医院'}
        self.dir_pdfs = 'E:/zhihu_pdfs/'  # 末尾一定要加上 / , 否则将会自动使用\做填充, 路径会出现问题
        self.identify = CurIdentify()
        # self.mongo_zw_all = MongoStore('wfhy_update','zw_all')
        self.mongo_zw_commit = MongoStore('wfhy_commit','zw_commit')
        self.redis_zw = ZwRedis()
        self.log = FrameLog('zw_cnki_re').get_log()
        self.retry_getsearchsql = 1
        self.redownpdf = ReDownPdf()
        self.redown_retry = 1

    def get_userinfo(self):

        userinfo = random.choice(self.userinfo)
        return userinfo

    def login(self):
        self.log.info('开始登录,请稍等...')
        time.sleep(1)
        userinfo = self.get_userinfo()
        print('当前用户信息为: ', userinfo)
        self.log.info('当前用户信息为: ', userinfo)
        username = userinfo['username']
        password = userinfo['password']
        img_retry = 1
        imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
        self.log.info('请求并识别验证码!!')
        res = self.session.get(imgcode_url, headers=self.headers_init)
        with open('imgcode.jpg', 'wb') as f:
            f.write(res.content)
        code_str = self.get_checkcode('imgcode.jpg')
        print('验证码字符串为: ', code_str)
        self.log.info('验证码识别结果为: {}'.format(code_str))
        time_ = int(time.time() * 1000)
        url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&checkCode={}&p=0&_={}'.format(
            username, password, code_str, time_)
        res = self.session.get(url, headers=self.headers_init)
        if '验证码不正确' in res.text:
            if img_retry <= 8:
                print('验证码识别出错, 正在重新识别, 请稍后!!!')
                self.log.info('验证码识别出错, 正在发起请求进行识别重新识别, 请稍后!!!')
                self.login()
                time.sleep(2)
        elif '登录失败，没有该用户' in res.text:
            print('请确认账号密码!')
            self.log.info('登录失败,请确认账号密码,我将发起重新登录!!')
        elif '登录成功' not in res.text:
            print(res.text)
            self.log.info('恭喜你登录成功!!')
        else:
            print('登录成功!!')

    def get_checkcode(self, img):

        ocr = ddddocr.DdddOcr(old=True)
        # 第一个验证截图保存：verification_code_1.png
        with open(img, 'rb') as f:
            image = f.read()
        res = ocr.classification(image)
        return res

    def get_searchsql(self):

        url = 'https://kns.cnki.net/kns8/defaultresult/index'
        self.session.get(url, headers=self.headers_init)
        self.login()
        cookie_dblang = {
            "dblang": "ch"
        }
        self.session.cookies.update(cookie_dblang)

        data = {
            'IsSearch': 'true',
            'QueryJson': '{"Platform":"","DBCode":"CFLS","KuaKuCode":"CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD","QNode":{"QGroup":[{"Key":"Subject","Title":"","Logic":1,"Items":[{"Title":"' +
                         self.searchinfo['title'] + '","Name":"AF","Value":"' + self.searchinfo[
                             'keywords'] + '","Operate":"%"}],"ChildItems":[]}]}}',
            'PageName': 'defaultresult',
            'DBCode': 'CFLS',
            'KuaKuCodes': 'CJFQ,CCND,CIPD,CDMD,BDZK,CISD,SNAD,CCJD,GXDB_SECTION,CJFN,CCVD',
            'CurPage': 1,
            'RecordsCntPerPage': 20,
            'CurDisplayMode': 'listmode',
            'CurrSortField': 'PT',
            'CurrSortFieldType': 'desc',
            'IsSentenceSearch': 'false',
            'Subject': ''
        }

        # 需请求两次列表第一页:  第一次获取到正常的无排序列表数据, 第二次获取根据日期排序的列表数据

        # 第一次获取到正常的无排序列表数据, 可获取第一列表页数据, 并可取出 searchsql作为第一次根据日期排序请求的参数

        res = self.session.post(self.list_url, data=data, headers=self.headers_list)
        if res.status_code == 200 and ('题名' in res.text and '发表时间' in res.text):
            html = etree.HTML(res.text)
            searchsql_data = html.xpath('//input[@id="sqlVal"]/@value')
            if searchsql_data:
                searchsql = searchsql_data[0]
                self.searchsql = searchsql
                self.retry_getsearchsql = 0
        else:
            if self.retry_getsearchsql <= 3:
                self.retry_getsearchsql += 1
                print('当前是第 {} 次获取searchsql'.format(self.retry_getsearchsql))
                self.log.warning('当前是第 {} 次获取searchsql'.format(self.retry_getsearchsql))
                time.sleep(random.uniform(1,3))
                self.get_searchsql()
            else:
                print('3次获取searchsql未能拿到数据, 退出程序!!')
                self.log.CRITICAL('3次获取searchsql未能拿到数据, 退出程序!!')
                exit()


    def down_detail_pdf(self):

        self.get_searchsql()
        headers_detail = {

            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'

        }
        data = self.redownpdf.find_identify_data()
        for item in data:
            # 1代表请求成功
            flag_success = 1
            detail_url = item['detail_url']
            try:
                res = self.session.get(detail_url, headers=headers_detail,timeout=(10,20))
            except requests.exceptions.ConnectionError as e:
                flag_success = 0
                for i in range(3):
                    print('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                    self.log.error('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                    time.sleep(300)
                    self.get_searchsql()
                    try:
                        res = self.session.get(detail_url, headers=headers_detail, timeout=(10, 20))
                        if res.status_code == 200 and 'pdfDown' in res.text:
                            print('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                            self.log.info('详情页 {} 第 {} 次尝试请求成功!!'.format(detail_url,i))
                            flag_success = 1
                            break
                    except Exception as e:
                        flag_success = 0
                        print(repr(e))

            if flag_success == 0:
                print('当前详情页链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
                self.log.error('当前详情页链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
                continue
            if res.status_code == 200 and 'pdfDown' in res.text:
                detail_html = etree.HTML(res.text)
                pdf_url = detail_html.xpath('//a[@id="pdfDown"][1]/@href')[0]
                if 'javascript' not in pdf_url:
                    base_url = 'https://bar.cnki.net'
                    pdf_url_ = urljoin(base_url, pdf_url)
                    item['pdf_url'] = pdf_url_
                    items = self.download_pdf(item)
                    if items:
                        self.save(items)
                    else:
                        print('pdf文件多次请求失败, 休息10 min重新发起请求, 文件信息为: {}'.format(str(item)))
                        self.log.error('pdf文件多次请求失败, 休息10 min重新发起请求, 文件信息为: {}'.format(str(item)))
                        time.sleep(600)
                else:
                    print('详情链接中含有javascript, 应该是需要充钱付费的, 请查看, pdf链接地址为: {}'.format(pdf_url))
            else:
                print('详情页链接地址请求有问题, 状态不为200 或者页面内不含有pdfDown, 详情页链接地址为: {}'.format(detail_url))


    def downpdf(self,url):
        pass
        #     for i in range(retry_max):
        #         try:
        #             res = self.session.get(item['pdf_url'], headers=headers_pdf,timeout=(10,20))
        #             print('当前的文件大小为: {}'.format(res.headers['Content-Length']))
        #             print(res.text)
        #             time.sleep(15)
        #             if res.status_code == 200 and int(res.headers['Content-Length']) >= size_limit:
        #                 print('下载pdf文件大小超过了 100k, 正常下载, 文件名为: {},不再重复发起请求!!'.format(item['file_name']))
        #                 self.log.info('下载pdf文件大小超过了 100k, 正常下载, 文件名为: {}'.format(item['file_name']))
        #                 break
        #             else:
        #                 print('第 {} 次下载当前pdf文件,信息为: {},  大小不到100k, 折回重新下载, '.format(i,str(item)))
        #                 self.log.info('第 {} 次下载当前pdf文件,信息为: {},  大小不到100k, 折回重新下载, '.format(i,str(item)))
        #                 time.sleep(random.uniform(0,1))
        #
        #         except requests.exceptions.ConnectionError as e:
        #             flag_success = 0
        #             for i in range(3):
        #                 print('下载pdf文件链接异常, 等待5分钟后重新登录下载, 错误显示为: {}'.format(repr(e)))
        #                 self.log.error('下载pdf文件链接异常, 等待5分钟后重新登录下载, 错误显示为: {}'.format(repr(e)))
        #                 time.sleep(20)
        #                 self.get_searchsql()
        #                 try:
        #                     res = self.session.get(item['pdf_url'], headers=headers_pdf,timeout=(10,20))
        #                     if res.status_code == 200 and int(res.headers['Content-Length']) >= size_limit:
        #                         print('第 {} 次尝试请求成功!!'.format(i))
        #                         self.log.info('第 {} 次尝试请求成功!!'.format(i))
        #                         flag_success = 1
        #                         break
        #                 except Exception as e:
        #                     flag_success = 0
        #                     print(repr(e))
        #
        #     if flag_success == 0:
        #         print('当前pdf链接重发{}次请求, 依然请求失败, 跳过! 信息为: {},跳过,进入下一个pdf文件的下载!'.format(retry_max,str(item)))
        #         self.log.error('当前pdf链接重发{}次请求, 依然请求失败,  信息为: {},跳过,进入下一个pdf文件的下载!'.format(retry_max,str(item)))
        #         continue
        #     if res.status_code == 200 and int(res.headers['Content-Length']) >= size_limit:
        #         spider_date = datetime.now().strftime('%Y%m%d%H%M')
        #         time.sleep(random.uniform(1, 3))
        #         name = 'again_{}_{}_{}.pdf'.format(item['title'].replace('/', '_'), item['date'].replace(' ', '&'),spider_date)
        #         file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", name)
        #         item['file_name'] = file_name
        #         file_path = os.path.join(self.dir_pdfs, file_name)
        #         pdf_obj = open(file_path, 'wb')
        #         pdf_obj.write(res.content)
        #         pdf_obj.close()
        #         print('下载路径地址为: {}'.format(file_path))
        #         print('开始识别医生信息...')
        #         doctor_infos = self.identify.identify_pdf(file_path)
        #         print('识别结果为: ', doctor_infos)
        #         item.update(doctor_infos)
        #         print("添加医生信息后的数据为: ", item)
        #         # 更改mongo字段, 如果有手机号, 需要备份到mongo commit表中
        #
        #         print('这是重新请求cnki文件的item,  ',item)
        #         return item
    def download_pdf(self, item):

        headers_pdf = {
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'

        }
        print('当前的item为: ',item)

        flag_success = 1
        try:
            res = self.session.get(item['pdf_url'], headers=headers_pdf, timeout=(10,20))
        except requests.exceptions.ConnectionError as e:
            flag_success = 0
            for i in range(3):
                print('下载pdf文件链接异常, 等待5分钟后重新登录下载, 错误显示为: {}'.format(repr(e)))
                self.log.error('下载pdf文件链接异常, 等待5分钟后重新登录下载, 错误显示为: {}'.format(repr(e)))
                time.sleep(300)
                self.get_searchsql()
                try:
                    res = res = self.session.get(item['pdf_url'], headers=headers_pdf, timeout=(10,20))
                    if res.status_code == 200:
                        print('pdf文件 第 {} 次尝试请求成功!!'.format(i))
                        self.log.info('pdf文件 第 {} 次尝试请求成功!!'.format(i))
                        flag_success = 1
                        break
                except Exception as e:
                    flag_success = 0
                    print(repr(e))

        if flag_success == 0:
            print('当前pdf链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
            self.log.error('当前pdf链接重启3次请求, 依然请求失败, 跳过! 信息为: {}'.format(str(item)))
            return
        time.sleep(random.uniform(1, 3))
        name = '{}_{}_redown.pdf'.format(item['title'].replace('/', '_'), item['date'].replace(' ', '&'))
        file_name = re.sub('[’!"#$%\'()*+,/:;<=>?@，。?★、…【】《》？“”‘’！[\\]^`{|}~\s]+', "", name)
        item['file_name'] = file_name
        # print(res.Content_Content-Length)
        print(res.headers['Content-Length'])
        # exit()
        max_limit = 51200

        if res.status_code == 200 and (int(res.headers['Content-Length']) >= max_limit):
            # with open('{}/{}.pdf'.format(self.dir_pdfs,item['title'].replace('/','_')),'wb') as f:
            #     f.write(res.content)
            # need_pay 为0 代表不需要支付
            item['content_size'] = str(round(int(res.headers['Content-Length'])/1024/1024,2)) + 'M'
            item['need_pay'] = '无需支付'
            file_path = os.path.join(self.dir_pdfs,file_name)
            pdf_obj = open(file_path, 'wb')
            pdf_obj.write(res.content)
            pdf_obj.close()
            print('下载路径地址为: {}'.format(file_path))
            print('开始识别医生信息...')
            doctor_infos = self.identify.identify_pdf(file_path)
            print('识别结果为: ',doctor_infos)
            item.update(doctor_infos)
            item['re_down'] = '重新下载'
            print("添加医生信息后的数据为: ",item)

        else:

            print('重新下载失败第 {} 次 '.format(self.redown_retry))
            self.log.warning('重新下载失败第 {} 次 '.format(self.redown_retry))
            if self.redown_retry < 3:
                self.redown_retry += 1
                item = self.download_pdf(item)
                time.sleep(5)
            else:
                print('重新下载持续3次依然失败, 跳过当前这条链接地址')
                print('重新下载持续3次依然失败, 标题为: ', item['title'])
                self.log.error('重新下载持续3次依然失败, 标题为: {}'.format(str(item['title'])))
                item['status'] = 0
                self.redown_retry = 0
        return item


    def save(self,item):

        print('这是进入到save方法里面的item')
        if 'status' not in item:
            spider_date = datetime.now().strftime('%Y%m%d%H%M')
            item['spider_date'] = spider_date
            self.redownpdf.redown_update(item)
            if ('phones' in item) and item['phones']:
                print('发现新数据, 且存在手机号, 可以插入到commit表中')
                item['commit_status'] = '未提交'
                self.mongo_zw_commit.insert(item)
            else:
                print('检测到新数据, 但手机号为空, 不加入到commit表中')
        else:
            print('当前pdf重新下载三次都没成功, 不保存数据库')



    def run(self):

        # (首先获取列表页session, 接着登录, 接着获取列表页获取searchsql数据)(放到一起,生成session,当cookie过期时,可重复更新获取), 接着重复遍历列表页数据, 接着根据详情页链接获取pdf数据进行保存
        # page_items = self.get_page_list()
        # for page_item_data in page_items:
        #     self.download_detail_pdf(page_item_data)

        self.down_detail_pdf()