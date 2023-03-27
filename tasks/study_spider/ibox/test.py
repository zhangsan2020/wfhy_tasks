import base64
import json
import re
import time
import snappy
import requests
import execjs

session = requests.Session()
# b = new Uint8Array(s.stringToArrayBuffer(JSON.stringify({
#                                     method: c.method || "GET",
#                                     header: O,
#                                     body: v,
#                                     call_id: g
#                                 })))

# https://www.ibox.art/zh-cn/static/6f928581818083711e28.v1665479073343.js
# https://www.ibox.art/zh-cn/static/b277ec12fa7d5afb1d5b.v1665479073343.js
r = session.get('https://www.ibox.art/zh-cn/static/b277ec12fa7d5afb1d5b.v1665479073343.js')
print(r.text)
appid = re.findall('const r={appId:"(.*?)",',r.text)[0]
print(appid)

time_ = int(time.time() * 1000)
call_id = "0.6665500568418836_{}".format(time_)
# appid = "wxe77e91c2fdb64e85"
# # appid = "wxa2d0710b1323fd96"
# const r={appId:"wxa2d0710b1323fd96",
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
        "value": "61cf1eb7576d4c09846ff97fcb394faa"
    },
    {
        "key": "ib-trans-id",
        "value": "106bd7a743314b0c8edf95457aaa45ce"
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
        "value": call_id
    },
    {
        "key": "x-wx-resource-appid",
        "value": appid
    },
    {
        "key": "x-wx-container-path",
        "value": "/nft-mall-web/v1.2/nft/product/getProductDetail?albumId=100514152&gId=103814632"
    }
]
v = ''
method = 'GET'
data = {
    'method':method,
    'header':o,
    'body':'',
    'call_id':call_id
}
data_dumps = json.dumps(data)
print(data_dumps)
ctl = execjs.compile(open('./test.js','r',encoding='utf-8').read())
b = json.dumps(ctl.call('get_b',data_dumps))
print(b)
#
N = snappy.compress(b.encode())
print(N)
#
#
token_key_param = {
    "appid":appid,
    "data":{
        "qbase_api_name":"tcbapi_get_service_info",
        "qbase_req":"{\"client_random\":\"0.04320623742501506_1665283466120\",\"system\":\"\"}",
        "qbase_options":{
            "identityless":"true",
            "resourceAppid":appid,
            "resourceEnv":"ibox-3gldlr1u1a8322d4",
            "config":{
                "database":{
                    "realtime":{
                        "maxReconnect":5,
                        "reconnectInterval":5000,
                        "totalConnectionTimeout":"null"
                    }
                }
            },
            "appid":appid,
            "env":"ibox-3gldlr1u1a8322d4"
        },
        "qbase_meta":{
            "session_id":str(time_),
            "sdk_version":"wx-web-sdk/WEBDOMAIN_1.0.0 (1655460325000)",
            "filter_user_info":False
        },
        "cli_req_id":"{}_0.7452725579569792".format(time_)
    }
}
#
url = 'https://web-001.cloud.servicewechat.com/wxa-qbase/jsoperatewxdata'
# headers_options = {
#     "Host": "web-001.cloud.servicewechat.com",
#     "Connection": "keep-alive",
#     "Access-Control-Request-Method": "POST",
#     "Access-Control-Request-Headers": "content-type",
#     "Origin": "https://www.ibox.art",
#     "Sec-Fetch-Mode": "cors",
#     "Accept": "*/*",
#     "Sec-Fetch-Site": "cross-site",
#     "Referer": "https://www.ibox.art/zh-cn/item/?resell=1&id=100514130&gid=103702146",
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
# }
# r = session.options(url,headers=headers_options)
# print(r.text)
#
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'Referer': 'https://www.ibox.art/zh-cn/item/?resell=1&id=100514130&gid=103702146',
    'Content-Type': 'application/json; charset=UTF-8',
    'Host': 'web-001.cloud.servicewechat.com',
    'Origin': 'https://www.ibox.art',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors'
}
res = session.post(url,data=json.dumps(token_key_param),headers = headers)
json_data = json.loads(res.json()['data'])
token = json_data['token']
key = json_data['key']
timestamp = str(json_data['timestamp'])
# print(json_data)
# print(key)

ctl_1 = execjs.compile(open('./test1.js','r',encoding='utf-8').read())
data = ctl_1.call('getdata',key)
print(data)
newdata = base64.b64decode(data)
print(newdata)
# data_list = list(data.values())
# print(list(data.values()))
# with open('./test1.js',)
url_ = 'https://web-001.cloud.servicewechat.com/wxa-qbase/container_service?token={}'.format(token)
print(url_)
headers = {
    "Access-Control-Allow-Credentials": "true",
"Access-Control-Allow-Origin": "https://www.ibox.art",
# "Access-Control-Expose-Headers": "x-wx-compression, x-wx-call-id, x-wx-server-timing",
    "Content-Type": "application/octet-stream",
    "Host": "web-001.cloud.servicewechat.com",
    "Origin": "https://www.ibox.art",
    "Referer": "https://www.ibox.art/zh-cn/",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "X-WX-COMPRESSION": "snappy",
    "X-WX-ENCRYPTION-TIMESTAMP": str(timestamp),
    "X-WX-ENCRYPTION-VERSION": "2",
    "X-WX-LIB-BUILD-TS": "1655460325335",
    "X-WX-REQUEST-CONTENT-ENCODING": "JSON",
    "X-WX-RESPONSE-CONTENT-ACCEPT-ENCODING": "PB, JSON",
    "X-WX-USER-TIMEOUT": "30000",
    "Accept-Encoding": "gzip, deflate, br"
}

headers_2 = {
    'Content-Type': "application/octet-stream",
    'X-WX-COMPRESSION': "snappy",
    # AES秘钥key对应的时间戳
    'X-WX-ENCRYPTION-TIMESTAMP': str(timestamp),
    'X-WX-ENCRYPTION-VERSION': '2',
    'X-WX-LIB-BUILD-TS': '1655460325335',
    'X-WX-REQUEST-CONTENT-ENCODING': "JSON",
    'X-WX-RESPONSE-CONTENT-ACCEPT-ENCODING': "PB, JSON",
    'X-WX-USER-TIMEOUT': '30000'
}

headers_opt = {
    "Host": "web-001.cloud.servicewechat.com",
    "Connection": "keep-alive",
    "Access-Control-Request-Method":"POST",
    "Access-Control-Request-Headers": "content-type,x-wx-compression,x-wx-encryption-timestamp,x-wx-encryption-version,x-wx-lib-build-ts,x-wx-request-content-encoding,x-wx-response-content-accept-encoding,x-wx-user-timeout",
    "Origin": "https://www.ibox.art",
    "Sec-Fetch-Mode": "cors",
    "Accept": "*/*",
    "Sec-Fetch-Site": "cross-site",
    "Referer": "https://www.ibox.art/zh-cn/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br"
}
# res = session.options(url_,headers=headers_opt)
# print(res.text)
res = session.post(url_,data=newdata,headers=headers)
print(res.text)