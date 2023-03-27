import time

from selenium import webdriver
from task.chinesejournal.loginfromtsg import LoginTrun
from selenium.webdriver.common.by import By

class DownPdf():

    def __init__(self):

        self.driver = webdriver.Chrome()
        # self.driver.add_cookie(cookies)
        # driver.add_cookie({'name': 'foo', 'value': 'bar', 'path': '/'})
        # cookie_dict = {}
        self.driver.get('http://tsg211.com/')
        self.login = LoginTrun()
        self.session = self.login.login_page_turn()
        self.driver.get('http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/')
        cookies = self.session.cookies.get_dict()
        print(cookies)
        for name,value in cookies.items():
            self.driver.add_cookie({'name': name, 'value': value, 'path': '/', 'Domain':'.jingshi2015.com'})

        print('这是添加之后的cookies', self.driver.get_cookies())

    def down_pdf(self):

        self.driver.get('http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Search/Index?from=Qikan_Search_Index')
        time.sleep(3)
        self.driver.get('http://sdu.webvpn.jingshi2015.com:8383/http/77726476706e69737468656265737421f3e45596693379467718c7af9758/Qikan/Article/Detail?id=7106709442')
        time.sleep(2)
        if '下载PDF' in self.driver.page_source:
            self.driver.find_element(By.XPATH,'//a[contains(text(),"下载PDF")]').click()
        # self.driver.get('http://www.baidu.com')

if __name__ == '__main__':

    down = DownPdf()
    down.down_pdf()