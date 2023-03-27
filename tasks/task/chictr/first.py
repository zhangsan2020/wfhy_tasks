# import requests
#
# class ChiCtr():
# for i in range(1,3):
#     url = 'http://www.chictr.org.cn/searchproj.aspx?title=&officialname=&subjectid=&secondaryid=&applier=&studyleader=&ethicalcommitteesanction=&sponsor=&studyailment=&studyailmentcode=&studytype=0&studystage=0&studydesign=0&minstudyexecutetime=&maxstudyexecutetime=&recruitmentstatus=0&gender=0&agreetosign=&secsponsor=&regno=&regstatus=0&country=&province=&city=&institution=&institutionlevel=&measure=&intercode=&sourceofspends=&createyear=0&isuploadrf=&whetherpublic=&btngo=btn&verifycode=&page={}'.format(i)
#     res = requests.get(url)
#     print(res.text)

# import random
#
# print(random.uniform(5, 10))
import re

url = 'http://www.chictr.org.cn/showproj.aspx?proj=79427'
print(re.findall('=(\d+)', url)[0])