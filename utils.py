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
from database import Bar,Tie,Base,University

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


def get_gaozhong_content():
    contents = [
        '有没有高三学生暑假做网络兼职的，格物水滴在招高考志愿填报模拟APP业务推广员，想了解的可以百度搜索"格物水滴"了解一下',
        '找高三学生做业务网络推广，有时间的同学可以了解一下，http://promotion.anyanggewu.com/promote。',
        "有没有同学要做网络兼职的，百度搜“格物水滴”查看人才招聘页面了解详情！",
        "做兼职的同学看过来，小赚一笔，百度搜“格物水滴”了解招聘详情！",
        "高三有没有要一起暑假工的，有个推广app的工作需要的可以百度搜索“格物水滴”了解一下人才招聘情况",
        '高考模拟报考用格|物|水|滴|APP,可以和报考相同学校和专业的同学交流，看自己考上的机会有多大',
        '|物|水|滴|APP上面有高考报名的功能，在选择学校和专业后，可以和未来的大学同学交流，推荐试用。',
        '高考模拟报考上格物水滴app,与报考者互相交流，帮助你考上理想大学',
        '格|物|水|滴|app,高考志愿填报模拟专用',
        '格|物|水|滴|app助你考上理想大学',
        '高考志愿模拟填报必用|物|水|滴|app',
        '用|物|水|滴|app更容易考上理想的大学',
        '同学们，有没有人在用|物|水|滴|app模拟高考报名',
        '谢谢！',
        '不错',
        '顶一下',
        '人过留名',
        '好',
        '这个可以有',
        '求人不如求己，高考志愿模拟报考快用格物水滴app。百度搜索格物水滴.'
        '高考分数固然重要，但是使用高考志愿模拟报考软件模拟报考也很重要，百度搜索格物水滴.',
        '能不能考上好大学，用格物水滴APP看一下就知道了。',
        '加油',
        '希望大家都能考一个好大学',
        '高考志愿模拟填报可以用格物水滴试一下。'
        '其他报考同学都考多少分，上格物水滴app和大家交流一下，看下自己能不能考的上。',
        '上什么大学？可以用格物水滴app和同学们交流一下啊',
        '高三同学有没有要兼职的，格物水滴找app推广人员，百度搜格物水滴了解一下啊！',
        '一脸懵逼 不知道这贴再说什么',
        '找高三同学做兼职推广，有意者可以百度搜格物水滴了解一下招聘兼职情况。',
        '机不可失，失不再来，招聘高三同学兼职，百度搜格物水滴了解详情。',
        '曾经我也是这么想的',
        '高考都考多少分',
        '高考考不上要复读吗？',
        '考个好大学太难了,同学们，一起上格物水滴app交流一下吧',
        '读好专科还是赖本科？'
        '大家发挥怎么样？',
        '准备复习一年，来年再战吗？',
        '上格物水滴app看能考上什么好大学',
        '专业重要换是学校重要，这个可以上格物水滴app看一下怎么做选择。',
	]

    return contents[random.randint(0, len(contents)-1)]

def get_daxue_content():
    contents = [
        '高考模拟报考用格|物|水|滴|APP,可以和报考相同学校和专业的同学交流，看自己考上的机会有多大',
        '|物|水|滴|APP上面有高考报名的功能，在选择学校和专业后，可以和未来的大学同学交流，推荐试用。',
        '高考模拟报考上格物水滴app,与报考者互相交流，帮助你考上理想大学',
        '格|物|水|滴|app,高考志愿填报模拟专用',
        '格|物|水|滴|app助你考上理想大学',
		'高考志愿模拟填报必用|物|水|滴|app',
		'用|物|水|滴|app更容易考上理想的大学',
		'同学们，有没有人在用|物|水|滴|app模拟高考报名',
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

    for barName in get_all_ba_name('高等院校'):
        b = University(name=barName)
        session.add(b)
        session.commit()

