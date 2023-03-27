import json
import re
import time
import requests
import itertools
import datetime
from lxml import etree
from common import gen_md5
from db import *
# AES-ECB加密

#url='https://custominfo.cebpubservice.com/cutominfoapi/recommand/type/3/pagesize/10/currentpage/{}'.format(str(i))
import base64
import json
from pyDes import des, ECB, PAD_PKCS5


def get_list_url():
    # for i in range(1, 10):
    #     print(i)
    url = 'http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?dates=300&categoryId=88&page=4&showStatus=1'
    headers = {
        'Accept': 'text / html, application / xhtml + xml, application / xml',
        'Connection': 'keep-alive',
        'Cookie': 'JSESSIONID=BF3E6D727E61DCF92329E5DA76E90923; Hm_lvt_da6ebc493961b944c4bf10a22517a198=1676858342; Hm_lpvt_da6ebc493961b944c4bf10a22517a198=1676861787',
        'Host': 'hnztbkhd.fgw.henan.gov.cn',
        'Referer': 'http://hnztbkhd.fgw.henan.gov.cn/xxfbcms/search/bulletin.html?searchDate=1998-02-20&dates=300&word=&categoryId=88&industryName=&area=&status=&publishMedia=&sourceInfo=&showStatus=1&page=4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3947.100 Safari/537.36'
    }
    time.sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        html_respone = response.text
        # print(html_respone)
        lyurl_list = re.findall("href=\"javascript:urlOpen\('(.*?)'", html_respone)
        title_list = re.findall("<a href=\"javascript:urlOpen\('.*'\)\" title=\"(.*?)\">",html_respone)
        time_list  = re.findall("<td style=\"text-align: left;\" name=\"imgShow\" id=\"(.*?)\">", html_respone)
        # for pub_time in time_list:
        #     pass
        # for title in title_list:
        #     titles = title
        # for lyurl in lyurl_list:
        #     lyurl = lyurl
        for pub_time, title, lyurl in itertools.zip(time_list, title_list, lyurl_list):
            print(pub_time,title,lyurl)
            content ="""<a href="{}">点击查看附件信息</a>""".format(lyurl)
            files = '#{}&{}'.format(title + '.pdf', lyurl)

if __name__ == '__main__':
    get_list_url()


