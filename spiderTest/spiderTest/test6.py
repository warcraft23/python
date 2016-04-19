#coding:utf_8
#文件中获取cookie并访问

import urllib2
import cookielib


cookie = cookielib.MozillaCookieJar()
cookie.load("cookie.txt",ignore_discard=True,ignore_expires=True)

request = urllib2.Request("http://www.baidu.com")
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
response = opener.open(request)

print response.read()

 