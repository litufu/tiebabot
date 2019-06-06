import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from random import choice

from bduss import bdusses
import pandas as pd
from database import Bar, Tie,Base,Search
from tiebautils import check,client_thread_add,get_fid,client_Post,Post
from utils import get_gaozhong_content
# 数据库
engine = create_engine('sqlite:///tiebar.sqlite')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
con = engine.connect()#创建连接
bars = session.query(Bar).all()



# webdriver
chrome_options = Options()
chrome_options.add_argument(
    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(
    executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
    options=chrome_options)

def replay(title,kw,bduss,content):
    '''

    :param title: 回复含有title的帖子
    :param kw: 贴吧名字
    :param bduss: 用户cookie
    :param content: 回复内容
    :return:
    '''
    print(kw)
    driver.get(url='http://tieba.baidu.com/f?kw={}'.format(kw))
    time.sleep(3)
    links = driver.find_element_by_id('thread_list').find_elements_by_partial_link_text(title)
    if len(links) == 0:
        print('没有找到相关{}链接'.format(title))
    fid = get_fid(kw)
    for link in links:
        text = link.get_attribute('href')
        pattern = re.compile('.*/p/(\d+)')
        res = pattern.match(text)
        if res:
            tid = res[1]
            search_results = []
            if len(search_results) == 0:
                print('开始回复{}'.format(tid))
                res = client_Post(bduss, kw, tid, fid, content)
                if 'error_msg' in res:
                    print(res)
                    return False
                else:
                    print(res)
                    new_search = Search(tid=tid,has_reply=True)
                    session.add(new_search)
                    session.commit()
                    print('回复完成{}'.format(tid))
                    time.sleep(60)
                    return True


if __name__ == '__main__':
    daxue = pd.read_sql_table('daxue', con)
    daxues = list(daxue["name"])
    for i in range(60):
        print(i)
        try:
            name = choice(daxues)
            content = '报考{}的同学们，'.format(name, get_gaozhong_content())
            response = replay('报考',name,bdusses[1],content)
        except Exception as e:
            print(e)
    time.sleep(3601)



