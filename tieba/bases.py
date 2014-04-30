# -*- coding:utf-8 -*-
# by スノル
# 2014/03/20

import urllib
import urllib2
import cookielib
import re
import json
import md5
from sys import stdin, stdout
from time import sleep

def _get_md5(astr):
    m = md5.new()
    m.update(astr)
    return m.hexdigest()


class Tieba(object):
    postdata_re = re.compile(
        r'<input type=hidden.*?name=(.+?) .*?value=(.*?)[> ]')
    bduss_re = re.compile(r'BDUSS=(.+?);')
    verifycode_re = re.compile(r'<img.*src="(.*?)".*')
    fid_re = re.compile(r' name="fid" value="(\d+)"\/>')
    tbs_re = re.compile(r'forums":(.+?\])')
    # TODO: <li data-fn=....

    _LIMITED_TRY = 10

    def __init__(self, username=None, password=None, bduss=None, infoin=stdin, infoout=stdout):
        self.cookie_jar = cookielib.LWPCookieJar()
        self.load_cookie()
        self.set_info(username, password, bduss)
        cookie_support = urllib2.HTTPCookieProcessor(self.cookie_jar)
        self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        self.opener.addheaders[0] = ('User-agent', "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac\
 OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334\
 Safari/7534.48.3 TiebaClient/1.2.1.17")
        self.infoin = infoin
        self.infoout = infoout
        self.tbhome_str = None
        self.logged_in = False
        self.is_ready = False

    def set_info(self, username, password, bduss=None):
        self.username = username
        self.password = password
        self.bduss = bduss
        if bduss is not None:
            # TODO load a cookie from string.
            pass

    def get_sure(self):
        self.infoout.write("Sure to relogin?\n")
        return True if self.infoin.readline().lower()[:-1] in ('yes', 'sure', 'y') else False

    def verify_code(self, url):
        self.infoout.write("Enter the verify code:\n%s\n" % url)
        return self.infoin.readline()[:-1]

    def login(self, force=False):
        '''Log in.'''
        if len(self.cookie_jar) > 0 and not force:
            force = self.get_sure()
            if not force:
                return
        tmp = self.opener.open(
            "http://wappass.baidu.com/passport/login").read()
        params = {x[0]: x[1].strip().strip('"') 
            for x in Tieba.postdata_re.findall(tmp)}
        params["username"] = self.username
        params["password"] = self.password
        if tmp.find("verifycode") >= 0:
            params["verifycode"] = self.verify_code(
                Tieba.verifycode_re.findall(tmp))
        req = urllib2.Request(
            'http://wappass.baidu.com/passport/login',
            urllib.urlencode(params)
        )
        self.opener.open(req)
        # 验证码可能出错
        bduss_tmp = Tieba.bduss_re.findall(self.cookie_jar.as_lwp_str())
        if len(bduss_tmp) > 0:
            self.bduss = bduss_tmp[0]
        else:
            print bduss_tmp
            print self.cookie_jar
            raise TiebaError
        if self._validate_login() is None:
            self.login(True)
            return
        self.is_login = True
        self.save_cookie()

    def logout(self):
        self.cookie_jar.clear()
        self.opener.close()

    def get_ready(self):
        if self.is_ready:
            return
        if not self.logged_in:
            self.login()
        self.infoout.write("Getting ready...")
        self.imei = _get_md5(self.bduss)
        self.tbn = self.get_tb()
        self.tbs = self._validate_login()
        self.infoout.write("Done!\n")
    def all_check(self):
        self.get_ready()
        for i in xrange(self.tbn):
            check_in(self.tbn[i])
            sleep(5)

    def check_in(self, tb):
        self.get_ready()
        self.infoout.write("Check in %s..." % tb)
        base_url = "http://c.tieba.baidu.com/c/c/forum/sign"
        params = {
            "BDUSS": self.bduss,
            "_client_id": "wappc_1378485686660_60",
            "_client_type": "2",
            "_client_version": "4.2.2",
            "_phone_imei": self.imei,
            "fid": tb['fid'],
            "kw": tb['tb'],
            "net_type": 3,
            "tbs": self.tbs
        }
        strsign = ''
        for e1, e2 in params.items():
            strsign += '%s=%s' % e1, e2
        strsign += 'tiebaclient!!!'
        md5sign = _get_md5(strsign.upper())
        params['sign'] = md5sign
        req = urllib2.Request(base_url, params)
        ret = self.opener.open(req)
        try:
            ret = json.loads(ret.read())
            assert len(ret) > 0
        except:
            raise TiebaError
        if rec['error_code'] == 0:
            self.infoout.write("Done!\n")
        else:
            self.infoout.write("\n%s\n" % rec)

    def load_cookie(self):
        pass

    def save_cookie(self):
        pass

    def _validate_login(self):
        tbs_obj = json.loads(self.opener.open("http://tieba.baidu.com/dc/common/tbs").read())
        tbs = tbs_obj.get('tbs', None)
        is_login = tbs_obj.get('is_login', False)
        return tbs if is_login else None

    def _get_fid(self, tbname):
        i = 0
        url = "http://wapp.baidu.com/f?kw=" + urllib.quote(tbname)
        while i < self._LIMITED_TRY:
            retstr = self.opener.open(url)
            fid = Tieba.fid_re.findall(retstr.read())
            if len(fid) > 0:
                return fid[0]
        raise GetfidError

    def get_tb(self):
        self._get_tbhome()
        tbs = Tieba.tbs_re.findall(self.tbhome_str)
        #print self.tbhome_str
        if len(tbs) == 0:
            raise GettbsError
        tbs = json.loads(tbs[0])
        tbn = []
        for i in xrange(len(tbs)):
            now_tb = {
                'force': 0,
                'fid': tbs[i]['forum_id'],
                'tb': tbs[i]['forum_name'],
                'level': tbs[i].get('level_id', 0),
                'exp': tbs[i].get('cur_score', 0)
            }
            tbn.append(now_tb)
        if len(tbn) > 0:
            tbn.sort(Tieba._cmp_tbs)
        return tbn

    @staticmethod
    def _cmp_tbs(a, b):
        if a['exp'] < b['exp']:
            return True
        return False

    def _get_tbhome(self, force=False):
        if len(self.cookie_jar) == 0:
            raise NoCookieError
        if not force and self.tbhome_str is not None:
            return
        url = 'http://tieba.baidu.com/'
        retstr = self.opener.open(url)
        self.tbhome_str = retstr.read()
        return


class TiebaError(Exception):
    _mes = 'Unknown Error.'

    def __init__(self):
        Exception.__init__(self, self._mes)

class GetfidError(TiebaError):
    _mes = 'Failed to get fid.'

class GettbsError(TiebaError):
    _mes = 'Failed to get tbs.'

class NoCookieError(TiebaError):
    _mes = 'No cookies.'
