#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import random
import time
import hashlib
import re
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Bar,Tie,Base

engine = create_engine('sqlite:///tiebar.sqlite')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# baClassFirst : 贴吧大类 如高等院校、中小学
# baClassSecond: 贴吧二类 如广东地区、北京地区
# 获取二级类别
def get_second_ba_class(first_class):
    html = urlopen("http://tieba.baidu.com/f/index/forumpark?cn=&ci=0&"
                   "pcn={}&pci=0&ct=1&rn=20&pn=1".format(quote(first_class, encoding="utf-8")))
    bs = BeautifulSoup(html.read(), 'html.parser')
    return bs.find("ul", {"class": "class_list"}).find_all('li')


# 获取所有的吧名
def get_all_ba_name(first_class):
    second_classes = get_second_ba_class(first_class)
    for className in second_classes:
        print('-----{}-----'.format(className.get_text()))
        for i in range(1, 31):
            html = urlopen("http://tieba.baidu.com/f/index/forumpark?cn={}&ci=0&pcn="
                           "{}&pci=0&ct=1&st=new&pn={}"
                           .format(quote(className.get_text(), encoding="utf-8"),
                                   quote(first_class, encoding="utf-8"), i))
            bs = BeautifulSoup(html.read(), 'html.parser')
            for baInfo in bs.find_all('div', {"class": "ba_info"}):
                ba_name = baInfo.find("p", {"class": "ba_name"}).get_text()
                if len(ba_name) != 0:
                    yield ba_name[0:len(ba_name) - 1]


def get_title():
    titles = [
        '高三的同学进',
        '有没有今年参加高考的',
        '同学们都报考什么学校和专业',
        '同学一起来填报高考志愿',
        '今年参加高考的进',
        '高三的来'

    ]
    return titles[random.randint(0, len(titles)-1)]


def get_content():
    contents = [
        '有个水滴APP,上面可以和报考相同学校和专业的同学交流，可以看自己有没有机会考上',
        '发现有个水滴APP,上面有高考报名的功能，在选择学校和专业后，可以和未来的大学同学交流。',
        '有个水滴App,报名的同时就可以查看自己报名排行榜，看一下自己是否能被录取',
    ]

    return contents[random.randint(0, len(contents)-1)]


def get_reply():
    replaies = [
        '占座',
        '留名',
        '前排',
    ]

    return replaies[random.randint(0, len(replaies) - 1)]


def save_bar():
    # 添加所有的中学
    for barName in get_all_ba_name('中小学'):
        if '高' in barName or '中' in barName:
            b = Bar(name=barName)
            session.add(b)
            session.commit()

def get_name(bduss):
    # 网页版获取贴吧用户名
    headers = {
        'Host':'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Cookie': 'BDUSS='+bduss,
    }
    url = 'https://tieba.baidu.com/mo/q-'
    try:
        r = requests.get(url=url, headers=headers).text
        name = re.search(r">([\u4e00-\u9fa5a-zA-Z0-9]+)的i贴吧<", r).group(1)
    except Exception:
        name = None
    finally:
        return name

def get_tbs(bduss):
    # 获取tbs
    headers = {
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Cookie': 'BDUSS=' + bduss,
    }
    url = 'http://tieba.baidu.com/dc/common/tbs'
    return requests.get(url=url,headers=headers).json()['tbs']

def get_fid(bdname):
    # 获取贴吧对用的fourm id
    url = 'http://tieba.baidu.com/f/commit/share/fnameShareApi?ie=utf-8&fname='+str(bdname)
    fid = requests.get(url,timeout=2).json()['data']['fid']
    return fid

def Post(bduss, content, tid, fid, tbname):
    # 网页版回帖
    tbs = get_tbs(bduss)
    headers = {
        'Accept':"application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding':"gzip, deflate, br",
        'Accept-Language':"zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'Connection':"keep-alive",
        'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
        'Cookie': 'BDUSS='+bduss,
        'DNT':'1',
        'Host':'tieba.baidu.com',
        'Origin': 'https://tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
        'ie':'utf-8',
        'kw':tbname,
        'fid':fid,
        'tid':tid,
        'tbs':tbs,
        '__type__':'reply',
        'content':content,
    }
    url = 'https://tieba.baidu.com/f/commit/post/add'
    r = requests.post(url=url,data=data,headers=headers,timeout=2).json()
    return r

def get_kw(tid):
    # 通过tid获取贴吧名字
    headers = {
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    url = 'https://tieba.baidu.com/p/' + str(tid)
    res = requests.get(url=url, headers=headers,timeout=2).text
    kw = re.search("fname=\"([^\"]+)\"", res).group(1)
    return kw

def encodeData(data):
    SIGN_KEY = 'tiebaclient!!!'
    s = ''
    keys = data.keys()
    for i in sorted(keys):
        s += i + '=' + str(data[i])
    sign = hashlib.md5((s + SIGN_KEY).encode('utf-8')).hexdigest().upper()
    data.update({'sign': str(sign)})
    return data

def check(bduss):
    # 检查bduss是否失效
    headers = {
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Cookie': 'BDUSS=' + bduss,
    }
    url = 'http://tieba.baidu.com/dc/common/tbs'
    return requests.get(url=url,headers=headers).json()['is_login']


def client_thread_add(bduss, kw, fid, content, title):
    # 客户端发帖
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'ka=open',
        'User-Agent': 'bdtb for Android 9.7.8.0',
        'Connection': 'close',
        'Accept-Encoding': 'gzip',
        'Host': 'c.tieba.baidu.com',
    }

    data = {
        'BDUSS': bduss,
        '_client_type': '4',
        '_client_id': 'wappc_1550210478950_661',
        '_client_version': '9.7.8.0',
        '_phone_imei': '000000000000000',
        'anonymous': '1',
        'call_from': '2',
        'content': content,
        'entrance_type': '1',
        'fid': fid,
        'is_ad': '0',
        'kw': kw,
        'model': 'MI+5',
        'net_type': '1',
        'new_vcode': '1',
        'can_no_forum': '0',
        'tbs': get_tbs(bduss),
        'timestamp': str(int(time.time())),
        'vcode_tag': '11',
        'is_hide': '1',
        'is_feedback': '0',
        'reply_uid': 'null',
        'is_ntitle': '0',
        'title': title,
        'subapp_type': 'mini',
        'takephoto_num': '0',
    }
    data = encodeData(data)
    url = 'http://c.tieba.baidu.com/c/c/thread/add'
    a = requests.post(url=url, data=data, headers=headers, timeout=2).json()
    return a

if __name__ == '__main__':
    # bduss = "N-OTlydVdrNk1iSURtRXdXT3VmWmJpOC1DQXVGVWFFdkNWRjFYeEo2Q2owQlpkSVFBQUFBJCQAAAAAAAAAAAEAAAAkj9T0d2Fud3VmdXN1MDM3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKND71yjQ-9cUz"
    # print(get_tbs(bduss))
    # print(get_name(bduss))
    print(get_fid('篮球'))
