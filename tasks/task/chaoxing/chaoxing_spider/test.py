# def testExcept():
#     try:
#         str1 = 'fei'
#         int1 = 5
#         result = str1 / int1
#     except Exception as e:
#         print(e)
#         print(f'error file:{e.__traceback__.tb_frame.f_globals["__file__"]}')
#         print(f"error line:{e.__traceback__.tb_lineno}")
#
#
# testExcept()
import re

a = '郑益志，Tel：15067 181800；E-mail：zyznsfc@163.com'
b = 'wefwfhih你好好哦  156567616' \
    '3145 二封囧恩Joe发'
print(re.findall('(1[35678]\d{9})', (a+b).replace(' ','').replace('\n','').replace('\r\n','')))