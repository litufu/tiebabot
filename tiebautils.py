# -*- coding:utf-8 -*-
import requests
import re
import hashlib
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_tbs(bduss):
    # 获取tbs
    headers = {
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'Cookie': 'BDUSS=' + bduss,
    }
    url = 'http://tieba.baidu.com/dc/common/tbs'
    return requests.get(url=url,headers=headers).json()['tbs']

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

def get_at(bduss):
    data = {
        'BDUSS': bduss,
        '_client_type': '2',
        '_client_id': 'wappc_1534235498291_488',
        '_client_version': '9.7.8.0',
        '_phone_imei': '000000000000000',
        'from': '1008621y',
        'page_size': '3000',
        'model': 'MI+5',
        'net_type': '1',
        'timestamp': str(int(time.time())),
        'vcode_tag': '11',
    }
    data = encodeData(data)
    url = 'http://c.tieba.baidu.com/c/u/feed/atme'
    res = requests.post(url=url, data=data).json()
    return res

def get_favorite(bduss):
    # 客户端关注的贴吧
    returnData = {}
    i = 1
    data = {
            'BDUSS':bduss,
            '_client_type':'2',
            '_client_id':'wappc_1534235498291_488',
            '_client_version':'9.7.8.0',
            '_phone_imei':'000000000000000',
            'from':'1008621y',
            'page_no':'1',
            'page_size':'200',
            'model':'MI+5',
            'net_type':'1',
            'timestamp':str(int(time.time())),
            'vcode_tag':'11',
        }
    data = encodeData(data)
    url = 'http://c.tieba.baidu.com/c/f/forum/like'
    res = requests.post(url=url,data=data,timeout=2).json()
    returnData = res
    if 'forum_list' not in returnData:
        returnData['forum_list'] = []
    if res['forum_list'] == []:
        return {'gconforum':[],'non-gconforum':[]}
    if 'non-gconforum' not in returnData['forum_list']:
        returnData['forum_list']['non-gconforum'] = []
    if 'gconforum' not in returnData['forum_list']:
        returnData['forum_list']['gconforum'] = []
    while 'has_more' in res and res['has_more'] == '1':
        i = i + 1
        data = {
            'BDUSS': bduss,
            '_client_type': '2',
            '_client_id': 'wappc_1534235498291_488',
            '_client_version': '9.7.8.0',
            '_phone_imei': '000000000000000',
            'from': '1008621y',
            'page_no': str(i),
            'page_size': '200',
            'model': 'MI+5',
            'net_type': '1',
            'timestamp': str(int(time.time())),
            'vcode_tag': '11',
        }
        data = encodeData(data)
        url = 'http://c.tieba.baidu.com/c/f/forum/like'
        res = requests.post(url=url, data=data,timeout=2).json()
        if 'non-gconforum' in res['forum_list']:
            returnData['forum_list']['non-gconforum'].append(res['forum_list']['non-gconforum'])
        if 'gconforum' in res['forum_list']:
            returnData['forum_list']['gconforum'].append(res['forum_list']['gconforum'])
    return returnData


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



def get_qid(tid, floor):
    # 获取楼中楼的qid参数
    floor = int(floor)
    headers = {
        'Host': 'tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    }
    page = floor // 20 + 1
    url = 'https://tieba.baidu.com/p/'+str(tid)+'?pn='+str(page)
    res = requests.get(url=url,headers=headers,timeout=2).text
    qid = re.findall(r"post_content_(\d+)",res)
    try:
        return qid[floor-1]
    except Exception:
        return qid[len(qid)-1]

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


def LZL(bduss, content, kw, fid, tid, qid, floor):
    # 网页端楼中楼
    tbs = get_tbs(bduss)
    headers = {
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        'Connection': "keep-alive",
        'Content-Type': "application/x-www-form-urlencoded;charset=UTF-8",
        'Cookie': 'BDUSS=' + bduss,
        'DNT': '1',
        'Host': 'tieba.baidu.com',
        'Origin': 'https://tieba.baidu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    data = {
        'ie': 'utf-8',
        'kw': kw,
        'fid': fid,
        'tid': tid,
        'tbs': tbs,
        'quote_id':qid,
        'floor_num':floor,
        'content': content,
    }
    url = 'https://tieba.baidu.com/f/commit/post/add'
    r = requests.post(url=url, data=data, headers=headers,timeout=2).json()
    return r

def client_LZL(bduss, kw, fid, content, quote_id, tid):
    # 客户端楼中楼
    tbs = get_tbs(bduss)
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'ka=open',
        'User-Agent': 'bdtb for Android 9.7.8.0',
        'Connection': 'close',
        'Accept-Encoding': 'gzip',
        'Host': 'c.tieba.baidu.com',
    }

    data = {
            'BDUSS':bduss,
            '_client_type':'2',
            '_client_id':'wappc_1534235498291_488',
            '_client_version':'9.7.8.0',
            '_phone_imei':'000000000000000',
            'anonymous':'1',
            'content':content,
            'fid':fid,
            'kw':kw,
            'model':'MI+5',
            'net_type':'1',
            'new_vcode':'1',
            'post_from':'3',
            'quote_id':quote_id,
            'tbs':tbs,
            'tid':tid,
            'timestamp':str(int(time.time())),
            'vcode_tag':'12',
        }
    data = encodeData(data)
    url = 'http://c.tieba.baidu.com/c/c/post/add'
    res = requests.post(url=url,data=data,headers=headers,timeout=2).json()
    return res


def encodeData(data):
    SIGN_KEY = 'tiebaclient!!!'
    s = ''
    keys = data.keys()
    for i in sorted(keys):
        s += i + '=' + str(data[i])
    sign = hashlib.md5((s + SIGN_KEY).encode('utf-8')).hexdigest().upper()
    data.update({'sign': str(sign)})
    return data

def client_Post(bduss, kw, tid, fid, content):
    # 客户端回帖模式
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'ka=open',
        'User-Agent': 'bdtb for Android 9.7.8.0',
        'Connection': 'close',
        'Accept-Encoding': 'gzip',
        'Host': 'c.tieba.baidu.com',
    }

    data = {
        'BDUSS':bduss,
        '_client_type':'2',
        '_client_version':'9.7.8.0',
        '_phone_imei':'000000000000000',
        'anonymous':'1',
        'content':content,
        'fid':fid,
        'from':'1008621x',
        'is_ad':'0',
        'kw':kw,
        'model':'MI+5',
        'net_type':'1',
        'new_vcode':'1',
        'tbs':get_tbs(bduss),
        'tid':tid,
        'timestamp':str(int(time.time())),
        'vcode_tag':'11',
    }
    data = encodeData(data)
    url = 'http://c.tieba.baidu.com/c/c/post/add'
    a = requests.post(url=url,data=data,headers=headers,timeout=2).json()
    return a

def client_Sign(bduss, kw, fid, tbs):
    # 客户端签到
    url = "http://c.tieba.baidu.com/c/c/forum/sign"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'ka=open',
        'User-Agent': 'bdtb for Android 9.7.8.0',
        'Connection': 'close',
        'Accept-Encoding': 'gzip',
        'Host': 'c.tieba.baidu.com',
    }
    data = {
        "BDUSS": bduss,
        '_client_type':'2',
        '_client_version':'9.7.8.0',
        '_phone_imei':'000000000000000',
        "fid": fid,
        'kw': kw,
        'model':'MI+5',
        "net_type": "1",
        'tbs': tbs,
        'timestamp':str(int(time.time())),
    }
    data = encodeData(data)
    url = 'http://c.tieba.baidu.com/c/c/forum/sign'
    res = requests.post(url=url,data=data,timeout=1).json()
    return res


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

def get_tid(title,kw):
    chrome_options = Options()
    chrome_options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(
        executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
        options=chrome_options)
    driver.get(url='http://tieba.baidu.com/f?kw={}'.format(kw))
    time.sleep(3)
    link = driver.find_element_by_link_text(title)
    text = link.get_attribute('href')
    pattern = re.compile('.*/p/(\d+)')
    res = pattern.match(text)
    return res[1]




if __name__ == '__main__':
    from bduss import bdusses
    for bduss in bdusses:
        print(check(bduss))
