import base64

import requests
import json
import time
from Crypto.Cipher import AES
import httpx
import snappy
from ibox.js.PyExecJsDemo import get_bytes

key_url = 'https://web-001.cloud.servicewechat.com/wxa-qbase/jsoperatewxdata'


def get_headers(timestamp):
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
    return headers_2


def parse_compress_data():
    headers_list = []
    headers = {
        'Accept-Language': "zh-CN",
        'HOST': "api-h5-tgw.ibox.art",
        'IB-DEVICE-ID': "9ad7fdb73e434a6daf339a1e6298a0ca",
        'IB-PLATFORM-TYPE': "web",
        'IB-TRANS-ID': "42e46cf8a01d4e2587d2c96cd31e3f3d",
        'User-Agent': "",
        'X-WX-CALL-ID': "0.9000717952766866_1657361554363",
        'X-WX-CONTAINER-PATH': "/nft-mall-web/v1.2/nft/product/getResellList?type=0&origin=0&sort=0&page=1&pageSize=50",
        'X-WX-ENV': "ibox-3gldlr1u1a8322d4",
        'X-WX-EXCLUDE-CREDENTIALS': "unionid, cloudbase-access-token, openid",
        'X-WX-GATEWAY-ID': "gw-1-1g2n1gd143d56b56",
        'X-WX-REGION': "ap-beijing",
        'X-WX-RESOURCE-APPID': "wxe77e91c2fdb64e85",
        'content-type': "application/json",
    }
    call_id = "0.9000717952766867_" + str(int(time.time() * 1000))
    for k, v in headers.items():
        k = k.lower()
        if 'x-wx-call-id' == k:
            v = call_id
        headers_list.append({
            'key': k,
            'value': v
            # k: v
        })

    header_body = {
        "method": "GET",
        "header": headers_list,
        "body": "undefined",
        "call_id": call_id
    }

    header_body_arr = bytes(json.dumps(header_body).encode('utf-8'))
    header_body_c = snappy.compress(header_body_arr)
    return header_body_c


# 需要补位，str不是16的倍数那就补足为16的倍数
def add_to_16_byte(value):
    while len(value) % 16 != 0:
        value += b'\0'
    return value


def aes_encrypt(key_bytes, text):
    # 增加vi向量
    aes = AES.new(key_bytes, AES.MODE_CBC, key_bytes)
    bytes = aes.encrypt(add_to_16_byte(text))
    return bytes


def get_key_token():
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '626',
        'Content-Type': 'application/json',
        'Host': 'web-001.cloud.servicewechat.com',
        'Origin': 'https://www.ibox.art',
        'Pragma': 'no-cache',
        'Referer': 'https://www.ibox.art/',
        'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    data = {
        "appid": "wxe77e91c2fdb64e85",
        "data": {
            "qbase_api_name": "tcbapi_get_service_info",
            "qbase_req": "{\"client_random\":\"0.2826657173143865_1657318155306\",\"system\":\"\"}",
            "qbase_options": {
                "identityless": "true",
                "resourceAppid": "wxe77e91c2fdb64e85",
                "resourceEnv": "ibox-3gldlr1u1a8322d4",
                "config": {
                    "database": {
                        "realtime": {
                            "maxReconnect": 5,
                            "reconnectInterval": 5000,
                            "totalConnectionTimeout": "null"
                        }
                    }
                },
                "appid": "wxe77e91c2fdb64e85",
                "env": "ibox-3gldlr1u1a8322d4"
            },
            "qbase_meta": {
                # "session_id": "1657318155315",
                "session_id": str(int(time.time() * 1000)),
                "sdk_version": "wx-web-sdk/WEBDOMAIN_1.0.0 (1655460325000)",
                "filter_user_info": False
            },
            "cli_req_id": str(int(time.time() * 1000)) + "_0.5101258021009685"
        }
    }
    response = requests.post(url=key_url, headers=headers, json=data)
    content = json.loads(response.content)
    if content:
        data = json.loads(content.get('data'))
        token = data.get('token')
        key = data.get('key')
        timestamp = data.get('timestamp')
        print(token, key, timestamp)
        return key, token, timestamp


def get_request():
    base_url = 'https://web-001.cloud.servicewechat.com/wxa-qbase/container_service?token='
    key, token, timestamp = get_key_token()
    base_url += token

    data = parse_compress_data()
    key_bytes = get_bytes(key)
    aes_data = aes_encrypt(key_bytes, data)

    headers = get_headers(timestamp)
    with httpx.Client(http2=True) as client:
        response = client.post(base_url, headers=headers, content=aes_data)
        print(response.content)


if __name__ == '__main__':
    get_request()
