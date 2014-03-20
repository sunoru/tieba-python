
import urllib
import urllib2
import cookielib
import re

def _initurl(url, head="http://"):
    if url is None:
        return None
    if not url.startswith(head):
        return head + url
    return url

cookie_jar = cookielib.LWPCookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cookie_jar)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)


