import random
import time

import ddddocr
import requests
# from task.common.login_tsg90 import LoginTrun
from Chaojiying_Python_new.chaojiying import Chaojiying_Client


class CxCode():
    def __init__(self,session):

        self.img_url = 'http://qikan.chaoxing.j.hknsspj.cn/processVerifyPng.ac'
        # self.session = requests.Session()
        self.owning_account = '6849_超星1_西安交通大学'
        self.session = session
        self.img_path = 'F:/wanfang_tasks/tasks/task/chaoxing/chaoxing_spider/chaoxing_turn_code.png'
        # self.login_obj = LoginTrun(self.owning_account)
        # self.login_again()

    # def login_again(self):
    #
    #     if hasattr(self,'session') and self.session:
    #         print('存在 session, 开始清理session中的cookie, 并重新登录!!')
    #         self.session.cookies.clear()
    #         self.session = self.login_obj.login_page_turn(self.owning_account)
    #     else:
    #         print('不存在 session, 重新登录!!')
    #         self.session = self.login_obj.login_page_turn(self.owning_account)

    # def recognize_img(self):
    #
    #     ocr = ddddocr.DdddOcr()
    #     with open(self.img_path, 'rb') as f:
    #         img_bytes = f.read()
    #         f.close()
    #     code_num = ocr.classification(img_bytes)
    #     print('验证码为: ',code_num)
    #     return code_num

    def recognize_img(self):

        print('开始识别验证码!!')

        chaojiying = Chaojiying_Client('1029025432', 'jiamianwuke2018',
                                       '6e01a48912ce0a49b6dfc72f53bd3875')  # 用户中心>>软件ID 生成一个替换 96001
        im = open(self.img_path, 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        code_data = chaojiying.PostPic(im, 6001)
        print('验证码为: ',code_data)
        return code_data

    def get_img(self):

        for i in range(10):
            print('开始下载验证码!!')
            res = self.session.get(self.img_url)
            # print(res.text)
            if res.status_code == 200:
                with open(self.img_path,'wb') as f:
                    f.write(res.content)
                    f.close()
                break
            else:
                print('验证码请求失败!!')

    def check_code(self,code_data):

        print('开始验证验证码!!')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        text_path = 'F:/wanfang_tasks/tasks/task/chaoxing/chaoxing_spider/now_html.html'
        check_code_url = 'http://qikan.chaoxing.j.hknsspj.cn/processVerify.ac?ucode={}'.format(code_data)
        res = self.session.get(check_code_url,headers=headers,timeout=(20,30))
        print(res.text)
        if res.status_code == 200 and '请输入验证码' not in res.text:
            print('验证码验证成功!!')
            return 'ok'
        # with open(text_path,'w',encoding='utf-8') as f:
        #     f.write(res.text)
        #     f.close()

    def run(self):
        for i in range(10):
            self.get_img()
            code_data = self.recognize_img()
            check_status = self.check_code(code_data)
            if check_status == 'ok':
                print('跳转验证码验证成功!!')
                return self.session
            else:
                print('跳转验证码验证失败, 继续验证!!')
                time.sleep(random.uniform(3,5))

#
# if __name__ == '__main__':
#
#     code = CxCode()
#     code.get_img()