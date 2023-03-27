

import requests
import execjs
url = 'http://59.110.45.28/m/api/search'
ctl = execjs.compile(open('./decode_1.js','r',encoding='utf-8').read())
def getparam(message):
    encode_data = ctl.call('encode',message)
    if encode_data:
        data_info = encode_data.split('=')
    print(encode_data)
    print(data_info)
    data = {
        'data': data_info[1],
        'v': data_info[2]
    }
    return data
# 'text=晴天 - 周杰伦&page=7&type=migu'
for page in range(3,5):
    message = 'text=晴天 - 周杰伦&page={}&type=migu'.format(page)
    print('message: ',message)
    data = getparam(message)
    jsondata = requests.post(url,data=data).json()
    list_data = jsondata['data']['list']
    for item in list_data:
        name = item['name']
        url = item['url_128']
        res = requests.get(url)
        with open('{}.mp3'.format(name),'wb') as f:
            f.write(res.content)