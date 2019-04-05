#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote


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


for name in get_all_ba_name("高等院校"):
    print(name)
