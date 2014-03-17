
import urllib
import urllib2
import cookielib
import re

def _initurl(url, head="http://"):
    if url == None:
        return None
    if not url.startswith(head):
        return head + url

class Poster():
    def __init__(self, post_url, host_url=None):
        cookie_jar = cookielib.LWPCookieJar()
        cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
        
        self.opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        self.host_url = _initurl(host_url)
        self.post_url = _initurl(post_url)
        self.cookie = None
        self.host_page = None
        self.post_page = None
    
    def open_host_url(self):
        self.host_page = self.opener.urlopen(host_url).read()

    def close_all(self):
        pass

