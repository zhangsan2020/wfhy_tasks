import requests


class ChictrSlide():

    def __init__(self):

        session = requests.Session()

    def get_slide(self):

        headers = {
                    "Host": "www.chictr.org.cn",
                    "Connection": "keep-alive",
                    "sec-ch-ua": "\"Not_A Brand\";v=\"99\", \"Google Chrome\";v=\"109\", \"Chromium\";v=\"109\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "zh-CN,zh;q=0.9"
                }
        res = requests.get('https://www.chictr.org.cn/showproj.aspx?proj=1',headers=headers)
        res.encoding = 'utf-8'
        if '滑动验证页面' in res.text:
            print('进入滑动验证页面!')
        else:
            print('正常请求到数据')
        print(res.text)

if __name__ == '__main__':

    slide = ChictrSlide()
    slide.get_slide()