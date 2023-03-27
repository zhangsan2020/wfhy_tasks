import json
import time

from .loginfromtsg import LoginTrun


class ChinaJournal(LoginTrun):

    def __init__(self):
        super().__init__()
        # self.enterlist_url = 'http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=index'
        # self.turn_url()
        self.login_page_turn()


    def enterlist(self):
        # 先登录跳转
        self.first_list_url = self.login_after_url + 'Qikan/Search/Index?from=index'
        print('这是first_list_url',self.first_list_url)
        # 发起从中文期刊平台首页进入到列表页的请求
        headers = {
                    "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                    "Connection": "keep-alive",
                    "Content-Length": "110",
                    "Cache-Control": "max-age=0",
                    "Upgrade-Insecure-Requests": "1",
                    "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Referer": self.login_after_url,
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
        data = {
            "key": "Y=手术",
            "isNoteHistory": "1",
            "isLog": "1",
            "indexKey": "手术",
            "indexIdentifier": "Y"
        }

        res = self.session.post(self.first_list_url, data=data, headers=headers)
        # print(res.text)
        if '共找到' in res.text:
            print('已进入到列表页, 开始分页获取数据!!')
            print(res.text)
            print('这是要看的cookies: ',self.session.cookies)

        else:
            print('没有进入到列表页, 重新发起请求')
            # time.sleep(3)
            time.sleep(5)
            self.enterlist()
        # self.get_page_list(refer_url)

    def before_page_list(self):

        # time_ = int(time.time()*1000)
        # vpn_url = 'http://jiangnan.webvpn.jingshi2015.com:8181/wengine-vpn/cookie?method=get&host=cstj.cqvip.com&scheme=http&path=/Qikan/Search/Index&vpn_timestamp={}'.format(time_)
        # headers_1 = {
        #         "Host": "jiangnan.webvpn.jingshi2015.com:8181",
        #         "Connection": "keep-alive",
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        #         "Accept": "*/*",
        #         "Referer": self.first_list_url,
        #         "Accept-Encoding": "gzip, deflate",
        #         "Accept-Language": "zh-CN,zh;q=0.9",
        #         # "Cookie": "wengine_vpn_ticketwebvpn1_jiangnan_edu_cn=ceb2344fdd6abf03; refresh=1;"
        #     }
        # res = self.session.get(vpn_url,headers=headers_1)
        # print('这是获取vpn数据得到的结果: ',res.text)
        #
        #
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/wengine-vpn/cookie?method=set&host=cstj.cqvip.com&scheme=http&path=/Qikan/Search/Index&ck_data=GW1gelwM5YZuT%3D53ythBDi1P40qqqDleoEEqagyphPGq0inx.GMlHoL2D_PpKxbB.dmeHCnLjEzFujlU2vYTTcW8nrOldpRTYvIwgi7ZJbNHmd1N8c8tCmRYaZuPvuBdPrNIruT9XJ4my32Ql7RU2M2EYk0ett6YCVWg7lxOHlJBe.N.bqucnuRzAwOmuGgYxk5wRhtsEktfz6RyfJRrH5Nuh_uTY0fHICqAVxV4fShJdYtk0eTYDbfBgkdi8d8EDERQUbjV2_94oAic3PlBmlpRjsSOT3tcLyKeP1KgQb6qxJL..9DPNJvo0xy6dm1Tr2FI6gruK74iWLqfdatUWDJe92LVtMxeNGe9i3RD.VFMdZ094W26ynFe1YA%3B%20path%3D%2F%3B%20expires%3DFri%2C%2016%20Dec%202022%2001%3A13%3A46%20GMT'
        headers_2 = {
                    "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                    "Connection": "keep-alive",
                    "Content-Length": "0",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                    "Accept": "*/*",
                    "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                    "Referer": self.first_list_url,
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
        res = self.session.post(url,headers=headers_2)
        print('这是之前在之前的结果: ',res.text)

        # url_1 = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Search/SearchList?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5wEqBQtNRhhpBHVwOKnjRHoZGJN4Wg4G2h1xsXWUqWyDw_RHwyj8WNOsN3uOM4Jll3Tk5SyLPKDwMMBl8tncYNJl6xjFhFf9YYHbPU0y_tERbrQLNr3ys9LJo9Wp3SjmG74LablZv5kt0YEsbVj1IRKS9XQ8q4s76zP.h4TK95FhsPqgQMbAZDXwIAlNMB.WnI62gbDJ1suU20BOZ4gQcFJyjoc7R2Du8hKAztTRPF_v8bsHDyapXgmI3SB9Gj_UpHkCKL2SjeMl5jB6AkslXuakaT7uhyXwtoNEP0R9CJ_qrCxqHhTQmGiGy_c_s_IhPwPtUmWpYAYrTCvMo9Ewarj6P_n_YsU6gmW4gsvL9X0g8U1Inctd3qzM5N64eVqeV7tHyU6I8Q8YZliBHu6RyHA'
        # data =
        # self.session.post(url_1)


        # url = '{}CheckRequest/IsVerificationPass?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5AQIEtywzR1XIZvF1DI.CEBaOJLvubrRHI9KXwS5i.fQE9EMtE8A55Lqx26AeNQdSrypzSPBoa0N31c7WrLWRVv7qTQo5hpgdGNU.4V2pL.kbUS6YjdIV5q.xLjeTgeSmjfZtyySia0xQFy1V1MmWxERlbLMwIbqCF3Jmsh3tIPQ9MIcobjFQz9OYJmUSQa2KbH_Pvns94E5TgwitTeFD4Hlf7kfLgjH6EjYeN4bgnl5UOCKLTQU9cktqBT4XXWHdxOF7nJdZn.B7ps.mIQ27OJQ8nuGVlVnVld9I1yIEghwrqCwUmjc79qdNoUC7lSd7jQ1Fmk8a8I8Yv102rxouEym.uD0VXmZHYzFCG98bxwLzCyNld7gD3qXMu_sPGtnM8A65y4TZE8NxEGCi7jvHCA'.format(self.login_after_url)
        # print(url,url)
        url = '{}CheckRequest/IsVerificationPass'.format(self.login_after_url)
        data = {
            'verificationCode': ''
        }
        # headers = {
        #         "Host": "jiangnan.webvpn.jingshi2015.com:8181",
        #         "Connection": "keep-alive",
        #         "Content-Length": "17",
        #         "Accept": "application/json, text/javascript, */*; q=0.01",
        #         "X-Requested-With": "XMLHttpRequest",
        #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        #         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        #         "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
        #         "Referer": self.login_after_url,
        #         "Accept-Encoding": "gzip, deflate",
        #         "Accept-Language": "zh-CN,zh;q=0.9"
        #
        #             # "Cookie": "wengine_vpn_ticketwebvpn1_jiangnan_edu_cn=ceb2344fdd6abf03; refresh=1; wengine_vpn_ticketwebvpn_sdu_edu_cn=b0d4ceec2d833da0; session_token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY3MDU3MTE2NCwiZXhwIjoxNjcwNTc0NzY0fQ.eyJ1c2VybmFtZSI6IjcxMDE0Mjg5In0.IiY2pdC_YM-S7lZsTZHMA1PTwE4BnkK7Ga6xeCJKYE-y-Rf0XULuzXF2TGjJlrguHKNl-Xcge6JrcbaUdbiQRg; refresh=1"
        #         }
        url = 'http://jiangnan.webvpn.jingshi2015.com:8181/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/CheckRequest/IsVerificationPass?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5TBKf6XFLClVlcPSLUtVH8SAtYIb30jttoVxfEDBP6XjMxbO5.dK3sWntgb61J8ezj4Jnzuyt5mWXRF7ZLGaHFFI1aOPRM3hx3NQFwytku_CKMyjKMLgZb3cmiFe_zQPlOXignTYcycyWJjBd.GM1G9TmIa9skQjCOamkXYebIlAPKNXGpeSAIT5XcTcfDLoaDI31xUiBadPE1lrZ0P26Je92deloJPwJunoaFpiWt5HbxqJl1WP4EoiAqWAJU9dXGMLKDdRcKJ98uBTLunNCyEYaElYXxpyaESXwN5FznRVec_DYAOGTIdYsK4PLk67qn0HJhg8pu2yzLOaZvdKXByKsQeJSTkGx4YZ5vKp14bsDFgRVEc8Vygwasa.0Gubyf1bZiqQ1L8M3zniCyz7U7G'
        print('这是确认URL: ',url)
        headers = {
                        "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                        "Connection": "keep-alive",
                        "Content-Length": "17",
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "X-Requested-With": "XMLHttpRequest",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                        "Referer": self.first_list_url,
                        "Accept-Encoding": "gzip, deflate",
                        "Accept-Language": "zh-CN,zh;q=0.9",
                        # "Cookie": "wengine_vpn_ticketwebvpn_sdu_edu_cn=14473137c7d8709c; refresh=1; session_token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY3MTQ5NjE3OSwiZXhwIjoxNjcxNDk5Nzc5fQ.eyJ1c2VybmFtZSI6IjcxMDE0Mjg5In0.FQRkxr947_cbaGs36QWuDjyjsT_CIgJXUcB9YWoUBc8Woc4KnjUNle8Lmf-NjrwfhwbyANMRdzUDvsKiTNB29g; wengine_vpn_ticketwebvpn1_jiangnan_edu_cn=83c914698898a36f; refresh=1"
                    }

        # headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'application/json, text/javascript, */*; q=0.01', 'X-Requested-With': 'XMLHttpRequest'}
        # self.session.cookies.clear(domain='www.tsg211.com')
        # self.session.cookies.set(name='refresh',value='1',domain='jiangnan.webvpn.jingshi2015.com')

        print('这是headers: ',headers)
        print(self.session.cookies)
        res = self.session.post(url,data=json.dumps(data),headers=headers)
        print('这是请求列表页之前的连接结果: ',res.text)
        print(res.status_code)










    def get_page_list(self):

        url = '{}Search/SearchList?vpn-12-o2-cstj.cqvip.com&G5tA5iQ4=5kwTy0KKERi4cNr2Y8536X83nLkcSTDgI2qNLo2uQx79YuIXTjN6Fw7D5hneluN2DAAKm3Cp.qNLjko_wyp1g16_QDLw4DaQO4tAju6Uc.lC02sBnfvrQjU9yloERxrnnfVcNiZ1_hedubzRAE.55VDxpK39rIPQb9cZukL77.1Ak6jD3iLI9TR2VDZOu1GgzY9wdKjd_NKGf6x.f0Md_SPxyNWIanNfSEK.1540swC6bDiyqzNrHf0DwTpt8Iq8Vd0k7Oa181MXDrUhF9ABfNpGy26FCpn2ipw7lUOuoWKxEoA_Vw7ZMGITAEvjr8BicNvZcR591VvWIusyhNSvrM30Up39wdAh9iJdjuhD7_RFnoZyr7.MnCPhcPBfr_TqHLpbUkSoy2XQBWZsHacZxvG'.format(self.login_after_url)
        # print(url)
        data = {'searchParamModel':'{"ObjectType":1,"SearchKeyList":[],"SearchExpression":null,"BeginYear":null,"EndYear":null,"UpdateTimeType":null,"JournalRange":null,"DomainRange":null,"ClusterFilter":"","ClusterLimit":0,"ClusterUseType":"Article","UrlParam":"Y=手术","Sort":"2","SortField":null,"UserID":"15856445","PageNum":1,"PageSize":20,"SType":null,"StrIds":null,"IsRefOrBy":0,"ShowRules":"  参考文献=手术  ","IsNoteHistory":0,"AdvShowTitle":null,"ObjectId":null,"ObjectSearchType":0,"ChineseEnglishExtend":0,"SynonymExtend":0,"ShowTotalCount":456979,"AdvTabGuid":""}'}
        headers = {
                "Accept": "text/html, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Content-Length": "884",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                # "Cookie": "wengine_vpn_ticketwebvpn1_jiangnan_edu_cn=ceb2344fdd6abf03; refresh=1; wengine_vpn_ticketwebvpn_sdu_edu_cn=b0d4ceec2d833da0; session_token=eyJhbGciOiJIUzUxMiIsImlhdCI6MTY3MDU3MTE2NCwiZXhwIjoxNjcwNTc0NzY0fQ.eyJ1c2VybmFtZSI6IjcxMDE0Mjg5In0.IiY2pdC_YM-S7lZsTZHMA1PTwE4BnkK7Ga6xeCJKYE-y-Rf0XULuzXF2TGjJlrguHKNl-Xcge6JrcbaUdbiQRg; refresh=1",
                "Host": "jiangnan.webvpn.jingshi2015.com:8181",
                "Origin": "http://jiangnan.webvpn.jingshi2015.com:8181",
                "Referer": self.first_list_url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest"
            }
        self.session.cookies.set(name='refresh',value='1',domain='jiangnan.webvpn.jingshi2015.com')
        print(self.session.cookies)
        res = self.session.post(url,data=json.dumps(data),headers=headers)
        print(res.text)
        print(res.status_code)

    def run(self):

        self.enterlist()
        self.before_page_list()
        # self.get_page_list()
