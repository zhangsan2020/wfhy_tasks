import json
import time
from Crypto.Cipher import AES
import execjs
import requests

class Ibox():

    def __init__(self):

        self.url_wxdata = 'https://web-001.cloud.servicewechat.com/wxa-qbase/jsoperatewxdata'
        self.session = requests.Session()

    def get_wxdata(self):

        time_ = str(int(time.time() * 1000))
        data = {
                "appid": "wxb5b2c81edbd4cf69",
                "data": {
                    "qbase_api_name": "tcbapi_get_service_info",
                    "qbase_req": "{\"client_random\":\"0.4085768411967976_1673322893376\",\"system\":\"\"}",
                    "qbase_options": {
                        "identityless": 'true',
                        "resourceAppid": "wxb5b2c81edbd4cf69",
                        "resourceEnv": "ibox-3gldlr1u1a8322d4",
                        "config": {
                            "database": {
                                "realtime": {
                                    "maxReconnect": 5,
                                    "reconnectInterval": 5000,
                                    "totalConnectionTimeout": 'null'
                                }
                            }
                        },
                        "appid": "wxb5b2c81edbd4cf69",
                        "env": "ibox-3gldlr1u1a8322d4"
                    },
                    "qbase_meta": {
                        "session_id": time_,
                        "sdk_version": "wx-web-sdk/WEBDOMAIN_1.0.0 (" + str(1655460325000) + ")",
                        "filter_user_info": False
                    },
                    "cli_req_id": "{}_0.23208947808707103".format(time_)
                }
            }
        print(json.dumps(data))
        headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Connection": "keep-alive",
                "Content-Length": "626",
                "Content-Type": "application/json",
                "Host": "web-001.cloud.servicewechat.com",
                "Origin": "https://www.ibox.art",
                "Referer": "https://www.ibox.art/",
                "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            }
        res = self.session.post(self.url_wxdata,data=json.dumps(data),headers=headers)
        jsopera_data = res.json()['data']
        self.request_info = json.loads(jsopera_data)
        print(jsopera_data)
        print(type(jsopera_data))

    def get_detail(self):

        self.get_wxdata()
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Length": "848",
            "Content-Type": "application/octet-stream",
            "Host": "web-001.cloud.servicewechat.com",
            "Origin": "https://www.ibox.art",
            "Referer": "https://www.ibox.art/",
            "sec-ch-ua": "\"Not?A_Brand\";v=\"8\", \"Chromium\";v=\"108\", \"Google Chrome\";v=\"108\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "X-WX-COMPRESSION": "snappy",
            "X-WX-ENCRYPTION-TIMESTAMP": str(self.request_info['timestamp']),
            "X-WX-ENCRYPTION-VERSION": "2",
            "X-WX-LIB-BUILD-TS": "1655460325335",
            "X-WX-REQUEST-CONTENT-ENCODING": "JSON",
            "X-WX-RESPONSE-CONTENT-ACCEPT-ENCODING": "PB, JSON",
            "X-WX-USER-TIMEOUT": "30000"
        }

        url = self.request_info['service_url']
        key = self.request_info['key']
        data = self.get_param(key)
        res = self.session.post(url,headers=headers,data=data)
        print('这是最终返回的结果',res.text)
        # data =
#         1655460325335

    def get_param(self,key):

        time_ = str(int(time.time() * 1000))
        o = [
            {
                "key": "x-wx-exclude-credentials",
                "value": "unionid, cloudbase-access-token, openid"
            },
            {
                "key": "x-wx-region",
                "value": "ap-beijing"
            },
            {
                "key": "x-wx-gateway-id",
                "value": "gw-1-1g2n1gd143d56b56"
            },
            {
                "key": "host",
                "value": "api-h5-tgw.ibox.art"
            },
            {
                "key": "accept-language",
                "value": "zh-CN"
            },
            {
                "key": "ib-device-id",
                "value": "bdec4a5ca11b4b9a9932a7a5e1dfab99"
            },
            {
                "key": "ib-trans-id",
                "value": "b78f7d91eadb4115856727517281680a"
            },
            {
                "key": "x-cloudbase-phone",
                "value": ""
            },
            {
                "key": "ib-platform-type",
                "value": "web"
            },
            {
                "key": "content-type",
                "value": "application/json"
            },
            {
                "key": "user-agent",
                "value": ""
            },
            {
                "key": "x-wx-env",
                "value": "ibox-3gldlr1u1a8322d4"
            },
            {
                "key": "x-wx-call-id",
                "value": "0.014912083836926104_{}".format(time_)
            },
            {
                "key": "x-wx-resource-appid",
                "value": "wxb5b2c81edbd4cf69"
            },
            {
                "key": "x-wx-container-path",
                "value": "/nft-mall-web/nft/contentList"
            }
        ]
        v = 'undefined'
        time_g = str(int(time.time() * 1000))
        g = '0.8025826435162247_{}'.format(time_g)
        ctl = execjs.compile(open('./ibox_new.js','r').read())
        data = ctl.call('get_params',key)
        print('这是x: ',data['x'])
        print('这是N:', data['N'])
        data_n_new = []
        data_x_new = []
        for k,v in data['N'].items():
            data_n_new.append(v)

        for k,v in data['x'].items():
            data_x_new.append(v)

        data_n = bytes(data_n_new)
        data_x = bytes(data_x_new)
        print('这是 data_n_new: ', data_n_new)
        print('这是 data_x_new: ', data_x_new)
        print('这是 data_n: ', data_n)
        print('这是 data_x: ', data_x)
        # return data_x,data_n
        data = self.aes_encrypt(data_x,data_n)
        print('最终参数data为: ',data)
        return data
    # 需要补位，str不是16的倍数那就补足为16的倍数
    def add_to_16_byte(self,value):
        while len(value) % 16 != 0:
            value += b'\0'
        return value

    def aes_encrypt(self,key_bytes, text):
        # 增加vi向量
        aes = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
        data = aes.encrypt(self.add_to_16_byte(text))
        print(data)
        return data

    def aes_(self):
        pass


if __name__ == '__main__':

    ibox = Ibox()
    # ibox.get_wxdata()
    # data = ibox.get_param()
    ibox.get_detail()