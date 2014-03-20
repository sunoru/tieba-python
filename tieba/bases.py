# -*- coding:utf-8 -*-
# by スノル
# 2014/03/20

import urllib
import urllib2
import cookielib
import re

class Tieba(object):

    def __init__(self):
        self.cookie_jar = cookielib.LWPCookieJar()
        self.username = self.password = self.content = ''
        # 待添加
        cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
        self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

    def setinfo(self, username, password):
        self.username = username
        self.password = password

    def login(self):
        '''Log in.'''
        # Uncompleted
        params = {
            }
        req = urllib2.Request(
            'http://',
            urllib.urlencode(params)
        )
        tmp = self.opener.open(req)

    def check_in(self, tbname):
        base_url = "http://c.tieba.baidu.com/c/c/forum/sign" 
        # Uncompleted

