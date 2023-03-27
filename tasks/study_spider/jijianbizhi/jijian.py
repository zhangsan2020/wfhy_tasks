import requests
import json

url = 'https://api.zzzmh.cn/bz/v3/getData'
session = requests.Session()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'chuck': '7912ff6715a34dd684e748e68b4bbe06',
    'content-type': 'application/json;charset=UTF-8',
    'referer': 'https://bz.zzzmh.cn/'
}
r = session.options(url)
print(r.text)
data = {"size":24,"current":4,"sort":0,"category":0,"resolution":0,"color":0,"categoryId":0,"ratio":0}
res = session.post(url,headers=headers,data=json.dumps(data))
print(res.text)