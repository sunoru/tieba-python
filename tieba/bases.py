# -*- coding:utf-8 -*-
# by スノル
# 2014/03/20

import urllib
import urllib2
import cookielib
import re
import md5

def __get_md5(astr):
    m = md5.new()
    m.update(astr)
    return m.hexdigest()

class Tieba(object):
    postdata_re = re.compile(r'<input type="?hidden"?.*name="?(.*)"?.*value="?(.*)"?.*')
    bduss_re = re.compile(r'BDUSS=(.+?);')
    verifycode_re = re.compile(r'<img.*src="(.*?)".*')

    def __init__(self, username=None, password=None, bduss=None):
        self.cookie_jar = cookielib.LWPCookieJar()
        self.load_cookie()
        self.content = ''
        self.set_info(username, password, bduss)
        cookie_support = urllib2.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        self.opener.addheaders[0] = ('User-agent', "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac\
            OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334\
            Safari/7534.48.3 TiebaClient/1.2.1.17")

    def set_info(self, username, password, bduss=None):
        self.username = username
        self.password = password
        self.bduss = bduss
        if bduss is not None:
            #self.cookie_jar.set_cookie("BDUSS
            pass

    def get_sure(self):
        print "Sure to relogin?"
        return True if raw_input().lower() in ('yes', 'sure', 'y') else False

    def verify_code(self, url):
        print "Enter the verify code:"
        print url
        return raw_input() 

    def login(self, force=False):
        '''Log in.'''
        if len(self.cookie_jar) > 0 and not force:
            force = self.get_sure()
            if not force:
                return
        tmp = self.opener.open("http://wappass.baidu.com/passport/login").read()
        params = {x[0]: x[1] for x in Tieba.postdata_re.findall(tmp, tmp.find('method=POST'))
            if x[1] != ''}
        params["username"] = self.username
        params["password"] = self.password
        if tmp.find("verifycode") >= 0:
            params["verifycode"] = self.verify_code(Tieba.verifycode_re.findall(tmp))
        req = urllib2.Request(
            'http://wappass.baidu.com/passport/login',
            urllib.urlencode(params)
        )
        # 验证码可能出错
        self.content = self.opener.open(req)
        self.bduss =  Tieba.bduss_re.findall(self.cookie_jar.as_lwp_str())[0]
        self.save_cookie()

    def logout(self):
        self.cookie_jar.clear()
        self.opener.close()

    def check_in(self, tbname):
        base_url = "http://c.tieba.baidu.com/c/c/forum/sign"
        params = {
            "BDUSS": self.bduss,
            "_client_id": "wappc_1378485686660_60",
            "_client_type": "2",
            "_client_version": "4.2.2",
            "_phone_imei": __get_md5(self.bduss),
            "fid": $fid,
            "kw": $tb,
            "net_type": 3,
            "tbs": $tbs
        }

    def load_cookie(self):
        pass

    def save_cookie(self):
        pass

    @staticmethod
    def get_fid(tieba_name):
        while True:
            url = "http://wapp.baidu.com/f?kw=" + urllib.quote(tieba_name)
        # TODO

