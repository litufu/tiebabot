#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import random
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
        '可以啊',
        '不错不错',
        '这个可以有',
    ]

    return replaies[random.randint(0, len(replaies) - 1)]


def save_bar():
    # 添加所有的中学
    for barName in get_all_ba_name('中小学'):
        if '高' in barName or '中' in barName:
            b = Bar(name=barName)
            session.add(b)
            session.commit()

