# -*- coding:utf-8 -*-
# by スノル
# 2014/03/20

import urllib
import urllib2
import cookielib
import re

class Tieba(object):
    mre = re.compile(r'<input type="?hidden"?.*name="?(.*)"?.*value="?(.*)"?.*')
    rq = r'<img.*src="(.*?)".*'

    def __init__(self, username='', password=''):
        self.cookie_jar = cookielib.LWPCookieJar()
        self.load_cookie()
        self.content = ''
        self.set_info(username, password)
        cookie_support = urllib2.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        self.opener.addheaders[0] = ('User-agent', "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac\
            OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334\
            Safari/7534.48.3 TiebaClient/1.2.1.17")

    def set_info(self, username, password):
        self.username = username
        self.password = password

    def login(self, force=False):
        '''Log in.'''
        while (len(self.cookie_jar) > 0 and force is False):
            print "Sure to relogin?"
            force = bool(raw_input())
        tmp = self.opener.open("http://wappass.baidu.com/passport/login").read()
        params = {x[0]: x[1] for x in Tieba.mre.findall(tmp, tmp.find('method=POST'))
            if x[1] != ''}
        params["username"] = self.username
        params["password"] = self.password
        if tmp.find("verifycode") >= 0:
            print "Enter the verify code:"
            print re.findall(Tieba.rq, tmp)
            params["verifycode"] = raw_input()
        req = urllib2.Request(
            'http://wappass.baidu.com/passport/login',
            urllib.urlencode(params)
        )
        # 验证码可能出错
        self.content = self.opener.open(req)
        self.save_cookie()

    def check_in(self, tbname):
        base_url = "http://c.tieba.baidu.com/c/c/forum/sign"
        # Uncompleted
    
    def load_cookie(self):
        pass
    def save_cookie(self):
        pass

