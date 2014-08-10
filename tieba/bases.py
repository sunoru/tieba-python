# -*- coding:utf-8 -*-
# by スノル
# 2014/03/20

import urllib
import urllib2
import re
import json
import hashlib
from time import sleep


def _get_md5(astr):
    m = hashlib.md5()
    m.update(astr)
    return m.hexdigest()

class Tieba(object):
    postdata_re = re.compile(
        r'<input type=hidden.*?name=(.+?) .*?value=(.*?)[> ]')
    bduss_re = re.compile(r'BDUSS=(.+?);')
    verifycode_re = re.compile(r'<img.*src="(.*?)".*')
    fid_re = re.compile(r' name="fid" value="(\d+)"\/>')
    tbq_re = re.compile(r'data-fid="(.+?)".*?data-start-app-param="(.+?)".*?level_(\d+?)"')
    # TODO: <li data-fn=....

    _LIMITED_TRY = 10

    sign_base_url = "http://c.tieba.baidu.com/c/c/forum/sign"

    def __init__(self, cookie, filter=None, interval=3):
        if not isinstance(cookie, str):
            raise NoCookieError
        self.cookie = cookie
        self.opener = urllib2.build_opener()
        self.opener.addheaders[0] = ('User-agent', "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac\
 OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334\
 Safari/7534.48.3 TiebaClient/1.2.1.17")
        self.opener.addheaders.append(('Cookie', self.cookie))
        bduss = Tieba.bduss_re.findall(self.cookie)
        if len(bduss) == 0:
            raise NoCookieError
        self.bduss = bduss[0]
        self.imei = _get_md5(self.bduss)
        self.tbhome_str = self.tbn = self.tbs = None
        self._isready = False
        self.filter = filter if filter is not None else Tieba._filter_all
        self.interval = interval

    def get_ready(self):
        self.tbn = self.get_tb()
        self.tbs = self._validate_login()
        self._isready = True

    def sign_all(self):
        if not self._isready:
            self.get_ready()
        for i in xrange(len(self.tbn)):
            print "%s" % self.tbn[i]['tb'],
            o = self.sign(self.tbn[i])
            if o == 0:
                pass
            else:
                assert(0)
            sleep(self.interval)

    def sign(self, tb):
        params = {
            "BDUSS": self.bduss,
            "_client_id": "wappc_1378485686660_60",
            "_client_type": "2",
            "_client_version": "4.2.2",
            "_phone_imei": self.imei,
            "fid": tb['fid'],
            "kw": tb['tb'],
            "net_type": '3',
            "tbs": self.tbs
        }
        strsign = ''
        for e1, e2 in params.items():
            strsign += e1 + '=' + e2
        md5sign = _get_md5(strsign + 'tiebaclient!!!').lower()
        params['sign'] = md5sign
        params = urllib.urlencode(params)
        ret = self.opener.open(Tieba.sign_base_url, params)
        try:
            ret = json.loads(ret.read())
            assert len(ret) > 0
        except:
            raise TiebaError
        if ret['error_code'] == 0:
            print("Done!\n")
        else:
            print("\n%s\n" % ret)
        return ret['error_code']

    def load_cookie(self):
        pass

    def save_cookie(self):
        pass

    def _validate_login(self):
        tbs_obj = json.loads(self.opener.open("http://tieba.baidu.com/dc/common/tbs").read())
        tbs = tbs_obj.get('tbs', None)
        is_login = tbs_obj.get('is_login', False)
        return str(tbs) if is_login else None

    def _get_fid(self, tbname):
        i = 0
        url = "http://wapp.baidu.com/f?kw=" + urllib.quote(tbname)
        while i < self._LIMITED_TRY:
            retstr = self.opener.open(url)
            fid = Tieba.fid_re.findall(retstr.read())
            if len(fid) > 0:
                return fid[0]
        raise GetfidError

    def get_tb(self, force=False):
        self._get_tbhome(force)
        tbq = Tieba.tbq_re.findall(self.tbhome_str)
        #print self.tbhome_str
        if len(tbq) == 0:
            raise GettbsError
        tbn = []
        for i in xrange(len(tbq)):
            now_tb = {
                'fid': tbq[i][0],
                'tb': tbq[i][1],
                'level': int(tbq[i][2])
            }
            tbn.append(now_tb)
        return self.filter(tbn)

    def _get_tbhome(self, force=False):
        if not force and self.tbhome_str is not None:
            return
        url = 'http://tieba.baidu.com/'
        retstr = self.opener.open(url)
        self.tbhome_str = retstr.read().replace('\n', '')

    @staticmethod
    def _filter_all(tbn):
        return tbn[:]

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
