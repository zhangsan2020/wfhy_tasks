import json
import time
import js2py
import execjs
import requests
import re
session = requests.Session()
res = session.get('https://www.ibox.art/zh-cn/static/a78e0def87b00e99666c.v1667470713293.js')
print(res.text)
appid = re.findall('authorize",appId:"(\w+)",responseType',res.text)[0]
print(appid)
time_ = int(time.time() * 1000)
call_id = "0.6665500568418836_{}".format(time_)
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
print(json_data)

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
    'body':'undefined',
    'call_id':call_id
}
print(data)
new_data = json.dumps(data,ensure_ascii=False)
ctl = execjs.compile(open('./ib_1.js','r',encoding='utf-8').read())
b_data = ctl.call('get_b',new_data)
print(b_data)
# param_1 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='
# func_get_b = '''
#     function get_b(y,e) {
#         for (var t = [], r = 0; r < e.length; r++) {
#             var n = e.charCodeAt(r);n < 128 ? t.push(n) : n < 2048 ? t.push(192 | n >> 6, 128 | 63 & n) : n < 55296 || n >= 57344 ? t.push(224 | n >> 12, 128 | n >> 6 & 63, 128 | 63 & n) : (r++,n = 65536 + ((1023 & n) << 10 | 1023 & e.charCodeAt(r)),t.push(240 | n >> 18, 128 | n >> 12 & 63, 128 | n >> 6 & 63, 128 | 63 & n))
#         }
#         return new Uint8Array(t).buffer
#     }
# '''
# get_b = js2py.eval_js(func_get_b)
# print(get_b(param_1,new_data))
# data = {
#
# }
# list_url = 'https://web-001.cloud.servicewechat.com/wxa-qbase/container_service?token={}'.format(token)
# session.post(list_url,data=data)