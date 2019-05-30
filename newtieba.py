# -*- coding:utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementClickInterceptedException
import json
from utils import get_title, get_content, get_reply
import random
from PIL import Image
from utils import session
from database import Bar, Tie
from content import content
from lzdm import code


headless = False

class BaiduSpider(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        chrome_options = Options()
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        if headless:
            chrome_options.add_argument('--headless')
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            options=chrome_options)
        self.driver.get(url='http://www.baidu.com')
        # self.set_cookie()
        self.is_login()

    def is_login(self):
        # 判断是否登录
        self.login()
        # html = self.driver.page_source
        # if html.find(self.username) == -1:  # 利用用户名判断是否登陆
        #     没登录 ,则手动登录
        #     print('你没有登录')
        #     self.login()

    def login_verify(self):
        try:
            try:
                # 电脑端
                verifycode = self.driver.find_element_by_id('TANGRAM__PSP_10__verifyCode')
            except Exception as e:
                # 手机端
                verifycode = self.driver.find_element_by_id('TANGRAM__PSP_3__verifyCode')
            print('请输入验证码')
            if verifycode:
                self.get_image()
                result = code('code{}.png'.format(self.username[0:4]))
                print(result['data'])
                v_code = result['data']['val']
                print(v_code)
                verifycode.clear()
                verifycode.send_keys(v_code)
                try:
                    submit = self.driver.find_element_by_id('TANGRAM__PSP_10__submit')
                except Exception as e:
                    submit = self.driver.find_element_by_id('TANGRAM__PSP_3__submit')
                submit.click()
                time.sleep(3)
        except Exception as e:
            print(e)
            print('无需输入人工验证码')

    def login(self):
        # 登陆
        print('start login manual')
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
        try:
            password = self.driver.find_element_by_id('TANGRAM__PSP_10__password')
        except Exception as e:
            password = self.driver.find_element_by_id('TANGRAM__PSP_3__password')
        password.send_keys(self.password)
        # 检查是否需要输入验证码,并登陆
        try:
            submit = self.driver.find_element_by_id('TANGRAM__PSP_10__submit')
        except Exception as e:
            submit = self.driver.find_element_by_id('TANGRAM__PSP_3__submit')
        submit.click()
        time.sleep(3)
        self.login_verify()
        # 输入手机验证码
        time.sleep(30)
        self.save_cookie()

    def save_cookie(self):
        '''保存cookie'''
        # 将cookie序列化保存下来
        f1 = open('{}.txt'.format(self.username), 'w')
        f1.write(json.dumps(self.driver.get_cookies()))
        f1.close

    def set_cookie(self):
        '''往浏览器添加cookie'''
        '''利用pickle序列化后的cookie'''
        try:
            f1 = open('{}.txt'.format(self.username))
            cookies = f1.read()
            cookies = json.loads(cookies)
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
            time.sleep(3)
        except Exception as e:
            print(e)
        finally:
            time.sleep(3)

    def get_snap(self):  # 对目标网页进行截屏。这里截的是全屏
        self.driver.save_screenshot('full{}.png'.format(self.username[0:4]))
        time.sleep(3)
        page_snap_obj = Image.open('full{}.png'.format(self.username[0:4]))
        return page_snap_obj

    def get_image(self):  # 对验证码所在位置进行定位，然后截取验证码图片
        try:
            img = self.driver.find_element_by_id('TANGRAM__PSP_10__verifyCodeImg')
        except Exception as e:
            img = self.driver.find_element_by_id('TANGRAM__PSP_3__verifyCodeImg')
        time.sleep(2)
        location = img.location
        print(location)
        size = img.size

        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']

        page_snap_obj = self.get_snap()
        if headless:
            image_obj = page_snap_obj.crop((left, top, right, bottom))
        else:
            image_obj = page_snap_obj.crop((left*1.25, top*1.25, right*1.25, bottom*1.25))
        image_obj.save('code{}.png'.format(self.username[0:4]))
        return image_obj  # 得到的就是验证码


    def focus(self,bar_name):
        '''
        关注贴吧
        :return:
        '''

        self.driver.get('http://tieba.baidu.com/f?kw={}'.format(bar_name))
        time.sleep(5)
        try:
            focus_btn = self.driver.find_element_by_class_name('islike_focus')
            focus_btn.click()
            time.sleep(2)
            close_btn = self.driver.find_element_by_class_name('dialogJclose')
            close_btn.click()
        except Exception as e:
            print(e)

    def convert_to_contents(self,content):
        '''
        将有换行符的内容随机分割成3到5部分。
        :param content: 原始内容
        :return: 分割后的内容列表，使用post_many发送
        '''
        contents = content.split('\n')
        contents_length = len(contents)
        if contents_length > 0:
            random_nums = []
            part_num = random.randint(3, 6)
            random_nums.append(0)
            for i in range(part_num):
                num_min = int(contents_length / part_num * i)
                num_max = int(contents_length / part_num * (i + 1)) - 1
                random_num = random.randint(num_min, num_max)
                random_nums.append(random_num)
            random_nums.append(contents_length)
            new_contents = ['<br>'.join(contents[random_nums[i]:random_nums[i + 1]]) for i in
                            range(len(random_nums) - 1)]
            return new_contents

    def post(self,bar_name, title, content):
        contents = content.split('\n')
        contents_length = len(contents)
        if contents_length > 0:
            new_contents = self.convert_to_contents(content)
            self.post_many(bar_name, title,new_contents)
        else:
            self.post_one(bar_name, title, content)

    def post_many(self,bar_name, title, contents):
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
        self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(contents[0]), ueditor_replace)
        time.sleep(5)
        # 点击提交
        button = self.driver.find_element_by_class_name('poster_submit')
        try:
            button.click()
        except ElementClickInterceptedException as e:
            pagesouce = self.driver.page_source
            if pagesouce.find('标题不能为空') != -1:
                print('没有标题')
                title_input.send_keys(title)
                button.click()
        time.sleep(5)
        # 判断是否发帖失败
        try:
            uiDialogWrapper = self.driver.find_element_by_class_name('uiDialogWrapper')
            fail_box_close = uiDialogWrapper.find_element_by_class_name('dialogJclose')
            fail_box_close.click()
            print("{}发帖失败".format(bar_name))
            time.sleep(300)
        except Exception as e:
            print('未显示发帖失败窗口:{}'.format(e))
            # 检查是否需要输入验证码
            try:
                self.driver.find_element_by_class_name('geetest_widget')
                print("输入人工验证码")
                input("输入人工验证码")
                # time.sleep(30)
            except Exception as e:
                # 如果没有发现输入验证码，则表明发帖成功
                print("无需输入验证码，发帖成功{}".format(e))
                time.sleep(10)
                # 查找刚发的贴子并进行回复
                post_title = self.driver.find_element_by_link_text(title)
                post_title.click()
                self.driver.refresh()
                time.sleep(8)
                for reply_content in contents[1:]:
                    # 输入内容
                    ueditor_replace = self.driver.find_element_by_id('ueditor_replace')
                    self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(reply_content), ueditor_replace)
                    # 点击提交
                    button = self.driver.find_element_by_class_name('poster_submit')
                    button.click()
                    self.driver.refresh()
                    time.sleep(5)
                    try:
                        self.driver.find_element_by_class_name('geetest_widget')
                        print("回帖需要输入人工验证码")
                        time.sleep(20)
                    except Exception as e:
                        print("无需输入验证码，回帖成功{}".format(e))
                sleep_time = random.randint(3, 5)
                time.sleep(sleep_time)

    def post_one(self, bar_name, title, cnt):
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
        self.driver.execute_script("arguments[0].innerHTML='<p>{}</p>'".format(cnt), ueditor_replace)
        time.sleep(5)
        # 点击提交
        button = self.driver.find_element_by_class_name('poster_submit')
        try:
            button.click()
        except ElementClickInterceptedException as e:
            pagesouce = self.driver.page_source
            if pagesouce.find('标题不能为空') != -1:
                print('没有标题')
                title_input.send_keys(title)
                button.click()
        try:
            fail_box_close = self.driver.find_element_by_class_name('uiDialogWrapper').find_element_by_class_name('dialogJclose')
            fail_box_close.click()
            print("{}发帖失败".format(bar_name))
            time.sleep(300)
        except Exception as e:
            print("发帖成功")
            sleep_time = random.randint(10, 15)
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

    # 账号
    accounts = [
        {'name':"wanwufusu037",'pwd':"123456abc"},
    ]
    # 登陆

    baidu = BaiduSpider('wanwufusu037', '123456abc')  # 你的百度账号，密码
    # 发帖
    for bar_obj in session.query(Bar).filter(Bar.hassend==False).all():
        barName = bar_obj.name
        print(barName)
        # post_title = '{}{}'.format(barName, get_title())
        # post_content = '{}的同学们，{}'.format(barName, get_content())
        # baidu.post(barName, post_title, post_content)
        baidu.focus(barName)
        # baidu.post(barName,'{}{}'.format(barName,get_title()), content)
        # bar_obj.hassend=True
        # session.commit()
    # 查看已发的帖子
    # baidu.get_ties()
    #  回复已经发布的帖子
    # baidu.reply()


