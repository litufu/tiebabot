# -*- coding:utf-8 -*-

import random
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from multiprocessing import Pool
from content import content
from database import Bar, Tie,Base
from tiebautils import check,client_thread_add,get_fid,client_Post
from utils import get_title

engine = create_engine('sqlite:///tiebar.sqlite')
Base.metadata.bind = engine

class Baidu(object):
    def __init__(self, bduss, no,length):
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        self.session = session
        self.bduss = bduss
        self.no = no
        self.length = length

    def post_content(self, kw, cnt,bar):
        '''
            res:{'opgroup': '0', 'pid': '125867227452', 'tid': '6147431000', 'msg': '发送成功', 'pre_msg': '经验 ', 'info': {'access_state': [], 'confilter_hitwords': [], 'need_vcode': '0', 'vcode_md5': '7555x/KllzCmyK+jbZ9frCkGvrEKm/lvsIWXiJNGWK/4Z2lzOtCPczDKRsCjCJnP', 'vcode_prev_type': '0', 'vcode_type': '0', 'pass_token': ''}, 'time': 1559196367, 'ctime': 0, 'logid': 367165643, 'error_code': '0', 'server_time': '569751'}
        '''
        contents = self.convert_to_contents(cnt)
        fid = get_fid(kw)
        title = '{}{}'.format(kw, get_title())
        if check(self.bduss):
            res = client_thread_add(self.bduss, kw, fid, contents[0], title)
            time.sleep(8)
            if res['msg'] != "发送成功":
                print('发帖失败{}'.format(kw))
            print('{}发帖成功'.format(kw))
            tid = res['tid']
            for cont in contents[1:]:
                client_Post(self.bduss, kw, tid, fid, cont)
                time.sleep(8)
            print('{}回帖成功'.format(kw))
            bar.hassend=True
            self.session.commit()
            time.sleep(80)

    def convert_to_contents(self,cnt):
        '''
        将有换行符的内容随机分割成3到5部分。
        :param content: 原始内容
        :return: 分割后的内容列表，使用post_many发送
        '''
        contents = cnt.split('\n')
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
            new_contents = ['\n'.join(contents[random_nums[i]:random_nums[i + 1]]) for i in
                            range(len(random_nums) - 1)]
            return new_contents

    def send_all(self, cnt):
        bars = self.session.query(Bar).filter(Bar.hassend == False).all()
        bars_length = len(bars)
        start = int(bars_length * (self.no / self.length))
        end = int(bars_length * ((self.no + 1) / self.length))
        for bar in bars[start:end]:
            self.post_content(bar.name, cnt,bar)
        self.driver.close()



def send(bduss,length,i):
    try:
        baidutieba = Baidu(bduss=bduss, length=length, no=i)
        baidutieba.send_all(content)
    except Exception as e:
        print(e)
        time.sleep(100)
        send()



if __name__ == '__main__':

    while True:
        bdusses = [
            "gySmxaVktPcFN3WXdvemZjZzBqWnptSHRPcWhaMH4wN2FPUGVnZjNCTlR-eFpkSVFBQUFBJCQAAAAAAAAAAAEAAAAkj9T0d2Fud3VmdXN1MDM3AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFNy71xTcu9cS3",
        ]
        length = len(bdusses)
        p = Pool(length)
        for i, bduss in enumerate(bdusses):
            p.apply_async(send, args=(bduss, length, i))
        print('Waiting for all subprocesses done...')
        p.close()
        p.join()
        print('All subprocesses done.')
        time.sleep(300)
