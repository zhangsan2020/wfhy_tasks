import requests
import execjs


class LiuMingYe():

    def __init__(self):
        self.url = 'http://59.110.45.28/m/api/search'
    #     with open('./data.js','r') as f:
    #         self.js_code = f.read()

    def get_data(self,text):

        js_code = execjs.compile(open('./data.js','r',encoding='utf-8').read())
        data = js_code.call('encode',text)
        print(data)
        return data

    def post_url(self,text):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }
        data = self.get_data(text)
        'text=周杰伦&page=1&type=migu'
        res = requests.post(self.url,data=data,headers=headers)
        print(res.text)
    def run(self):

        input_name = input('请输入歌手的姓名: ')
        data_text = 'text={}&page=1&type=migu'.format(input_name)
        self.post_url(data_text)



if __name__ == '__main__':

    lmy = LiuMingYe()
    lmy.run()
