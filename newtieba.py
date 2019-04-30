# -*- coding:utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle
from utils import get_title,get_content,get_reply
import random
from utils import session
from database import Bar,Tie

class BaiduSpider(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        chrome_options = Options()
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            options=chrome_options)
        self.driver.get(url='http://www.baidu.com')
        # self.set_cookie()
        # self.driver.refresh()
        time.sleep(3)
        self.is_login()

    def is_login(self):
        # 判断是否登录
        html = self.driver.page_source
        if html.find(self.username) == -1:  # 利用用户名判断是否登陆
            # 没登录 ,则手动登录
            print('你没有登录')
            self.login()

    def login(self):
        # 登陆
        print('start login manual')
        self.driver.refresh()
        try:
            login = self.driver.find_elements_by_css_selector('div[id=u1] a[class=lb]')[0]
        except Exception as e:
            login = self.driver.find_element_by_link_text('登录')
        login.click()
        time.sleep(3)
        username_login = self.driver.find_elements_by_css_selector('p.tang-pass-footerBarULogin')[0]
        time.sleep(2)
        username_login.click()
        try:
            # 电脑端
            username = self.driver.find_element_by_id('TANGRAM__PSP_10__userName')
        except Exception as e:
            # 手机端
            username = self.driver.find_element_by_id('TANGRAM__PSP_3__userName')
        username.send_keys(self.username)
        time.sleep(1)
        try:
            password = self.driver.find_element_by_id('TANGRAM__PSP_10__password')
        except Exception as e:
            password = self.driver.find_element_by_id('TANGRAM__PSP_3__password')
        password.send_keys(self.password)
        time.sleep(1)
        try:
            submit = self.driver.find_element_by_id('TANGRAM__PSP_10__submit')
        except Exception as e:
            submit = self.driver.find_element_by_id('TANGRAM__PSP_3__submit')
        submit.click()
        # 人工输入手机验证码
        time.sleep(30)
        self.save_cookie()

    def save_cookie(self):
        '''保存cookie'''
        # 将cookie序列化保存下来
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))

    def set_cookie(self):
        '''往浏览器添加cookie'''
        '''利用pickle序列化后的cookie'''
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
            print(e)

    def post(self, bar_name, title, content):
        self.driver.get('http://tieba.baidu.com/f?kw={}'.format(bar_name))
        time.sleep(5)
        # 将页面滚动条拖到底部
        js = "var q=document.documentElement.scrollTop=10000"
        self.driver.execute_script(js)
        time.sleep(3)
        # 输入标题
        title_input = self.driver.find_element_by_name('title')
        title_input.send_keys(title)
        time.sleep(3)
        # 输入内容
        ueditor_replace = self.driver.find_element_by_id('ueditor_replace')
        self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(content), ueditor_replace)
        time.sleep(3)
        # 点击提交
        button = self.driver.find_element_by_class_name('poster_submit')
        # button.click()
        sleep_time = random.randint(5, 15)
        time.sleep(sleep_time)

    def get_ties(self):
        self.driver.get('http://tieba.baidu.com/i/i/my_tie')
        tables = self.driver.find_elements_by_tag_name('table')
        for table in tables:
            bar_tag = table.find_element_by_class_name('nowrap').find_element_by_tag_name('a')
            bar_name = bar_tag.text[:-1]
            bars = session.query(Bar).filter(Bar.name == bar_name).all()
            if len(bars) == 0:
                bar = Bar(name=bar_name)
            else:
                bar = bars[0]
            tie_tag = table.find_element_by_class_name('wrap').find_element_by_tag_name('a')
            tie_url = tie_tag.get_attribute('href')
            tie = Tie(url=tie_url, bar_id=bar.id, bar=bar)
            session.add(tie)
            session.commit()

    def reply(self):
        ties = session.query(Tie).all()
        for tie in ties:
            if '高' in tie.bar.name or '中' in tie.bar.name:
                self.driver.get(tie.url)
                # 将页面滚动条拖到底部
                js = "var q=document.documentElement.scrollTop=10000"
                self.driver.execute_script(js)
                time.sleep(3)
                reply_content = get_reply()
                # 输入内容
                ueditor_replace = self.driver.find_element_by_id('ueditor_replace')
                self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(reply_content), ueditor_replace)
                time.sleep(3)
                # 点击提交
                button = self.driver.find_element_by_class_name('poster_submit')
                button.click()
                sleep_time = random.randint(5, 15)
                time.sleep(sleep_time)





if __name__ == '__main__':
    # 登陆
    baidu = BaiduSpider('litufu001', '123456abc')  # 你的百度账号，密码
    # 发帖
    for bar in session.query(Bar).all():
        barName = bar.name
        post_title = '{}{}'.format(barName, get_title())
        post_content = '{}的同学们，{}'.format(barName, get_content())
        baidu.post(barName, post_title, post_content)
    # 查看已发的帖子
    baidu.get_ties()
    #  回复已经发布的帖子
    baidu.reply()


