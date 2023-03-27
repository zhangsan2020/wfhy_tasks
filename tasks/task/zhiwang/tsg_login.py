
# 账号: 15210559392
# 密码: mengyao2016


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

# def login():
#
#     _ = int(time.time()*1000)
#     url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&p=0&_={}'.format(username,password,_)
#     res = session.get(url,headers=headers)
#     print(res.text)
#     print(session.cookies)

def login():

    img_retry = 1
    imgcode_url = 'https://login.cnki.net/TopLoginNew/api/loginapi/CheckCode?t=0.9807550126534068'
    res = session.get(imgcode_url,headers=headers)
    with open('imgcode.jpg','wb') as f:
        f.write(res.content)
    code_str = get_checkcode('imgcode.jpg')
    print('验证码字符串为: ',code_str)
    _ = int(time.time()*1000)
    url = 'https://login.cnki.net/TopLoginNew/api/loginapi/Login?callback=jQuery111309824996151701275_1664346351260&userName={}&pwd={}&isAutoLogin=true&checkCode={}&p=0&_={}'.format(username,password,code_str,_)
    res = session.get(url,headers=headers)
    if '验证码不正确' in res.text:
        if img_retry <= 5:
            print('验证码识别出错, 正在重新识别, 请稍后!!!')
            login()
            time.sleep(2)

    elif '登录失败，没有该用户' in res.text:
        print('请确认账号密码!')
    else:
        print('登录成功!!')
    return session
    # print(res.text)
    # print(session.cookies)

def get_checkcode(img):
    ocr = ddddocr.DdddOcr(old=True)
    # 第一个验证截图保存：verification_code_1.png
    with open(img, 'rb') as f:
        image = f.read()
    res = ocr.classification(image)
    return res

# get_checkcode()
# login()
# headers = {
#
#     'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
#     'Upgrade-Insecure-Requests': '1',
#     'sec-ch-ua-mobile': '?0',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
#     'sec-ch-ua-platform': 'Windows',
#     'Origin': 'https://kns.cnki.net',
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'Sec-Fetch-Site': 'same-origin',
#     'Sec-Fetch-Mode': 'cors',
#     'Sec-Fetch-User': '?1',
#     'Sec-Fetch-Dest': 'document',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Accept-Language': 'zh-CN,zh;q=0.9',
#     'Referer': 'https://kns.cnki.net/kns8/defaultresult/index'
# }
# url = 'https://kns.cnki.net/kns8/download?filename=nNHMz9UR5ITVI9CM2BFSrZHRHJmVSV0QRB1RYdVRldWasFVVkdGOlVGarkXQKJ3cjljdxIXSQl3TPFFV4ImRrRlS3M1KDJzZKdTd1sGeO9kU6hDbQpUQYl2T2UXU1pXavYXVBpUaP5mN2dVWThXQ5BTcvVDMwc2Q&tablename=CAPJDAY'
#
# res = session.get(url,headers=headers)
# print(res.text)