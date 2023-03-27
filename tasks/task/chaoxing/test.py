# from copy import copy
#
# a = [23]
# b = [24]
# a.extend(b)
# print(id(a))
# c = copy(a)
# print(id(c))
# from lxml import etree
# a = '''<div id="other">
#    <p class="meta" data-meta-name="中图分类号"><span class="key" data-meta-name="中图分类号.标题">中图分类号：</span>R749</p>
#    <p class="meta" data-meta-name="文献标识码"><span class="key" data-meta-name="文献标识码.标题">文献标识码：</span>B</p>
#    <p class="meta" data-meta-name="doi"><span class="key" data-meta-name="doi.标题">DOI：</span>10.3969/j.issn.1671-3141.2022.78.032</p>
#    <p class="meta" data-meta-name="引文格式"><span class="key" data-meta-name="引文格式.标题">本文引用格式：</span>姬晓花,叶盼,陈丁丁.陈丁丁主任医师治疗小儿抽动障碍常用药物经验[J].世界最新医学信息文摘,2022,22(078):160-164.</p>
#    <p class="meta" data-meta-name="作者简介"><span class="key" data-meta-name="作者简介.标题">作者简介：</span>第一作者：姬晓花（1995-），女，甘肃秦安，硕士研究生在读，主要研究方向：中医儿科防治肺系疾病。</p>
#    <p class="meta" data-meta-name="通信作者"><span class="key" data-meta-name="通信作者.标题">通信作者</span><span class="emphasis_bold">＊：</span>陈丁丁，男，职称：主任医师。</p>
#   </div>'''
# html = etree.HTML(a)
# author_infos = html.xpath('//p[@data-meta-name="作者简介"]/text()')
# if author_infos:
#     author_info = author_infos[0].strip()
#     print(author_info)
# else:
#     print('当前没有作者简介!! 连接地址为: {}')
import random
import time

import ddddocr
import requests

session = requests.Session()

def login_tsg():
    headers = {
        "Host": "www.90tsg.com",
        "Connection": "keep-alive",
        "Content-Length": "107",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://www.90tsg.com",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Referer": "http://www.90tsg.com/e/member/login/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    login_url = 'http://www.90tsg.com/e/member/doaction.php'
    for i in range(20):
        try:
            data = {
                'ecmsfrom': '',
                'enews': 'login',
                'tobind': 0,
                'username': '00966849',
                'password': '971152',
                'lifetime': 0,
                'Submit': '登    录'
            }
            res = session.post(login_url, data=data, headers=headers, timeout=(180, 360))

            if res.status_code == 200 and '登录成功' in res.text:
                print('90图书馆登录成功!!')
                return 1
            else:
                print('登录90tsg时返回数据异常, 稍等一会儿, 重新发起登录请求!!!')
                print(res.text)
                time.sleep(random.uniform(10, 20))
                session.cookies.clear()
        except:
            print('登录90tsg时出错, 稍等一会儿, 重新发起登录请求!!!')
            time.sleep(random.uniform(6, 12))
            session.cookies.clear()

        # print('连续第 {} 次登录出现异常'.format(i))


img_code_path = './testcode.jpg'
def get_img_data():
    img_url = 'http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/processVerifyPng.ac'
    headers = {
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        # "Cookie": "ishide=true; clientId=CIDa3df78c18d28da8c5f3fa4408885bc68; JSESSIONID=0B7253937FB02BD7BCAE407022CE5C8C; ddhgguuy_session=jq39cjjo35lu2faileb914tdg2",
        "Host": "nmg.jitui.me",
        # "Referer": "http://nmg.jitui.me/rwt/CXQK/https/PFVXXZLPF3SXRZLQQBVX633PMNYXN/processVerify.ac?ucode=axka",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    # print('当前验证码请求头为: ', headers_code)
    # self.session.cookies.clear()
    res = session.get(img_url, headers=headers, timeout=(10, 20))
    print(res.text)
    with open(img_code_path, 'wb') as f:
        f.write(res.content)
        f.close()


def recognize_img():
    ocr = ddddocr.DdddOcr()
    with open(img_code_path, 'rb') as f:
        img_bytes = f.read()
        f.close()
    code_num = ocr.classification(img_bytes)
    print(code_num)
    return code_num

def test_login():

    login_tsg()
    print(session.cookies.get_dict())
    get_img_data()
    # recognize_img()

test_login()