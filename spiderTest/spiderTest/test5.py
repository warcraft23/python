#coding:utf_8
#保存cookie,到文件

import urllib2
import cookielib

#cookie = cookielib.CookieJar();

filename = "cookie.txt"
cookie = cookielib.MozillaCookieJar(filename)

cookieHandler = urllib2.HTTPCookieProcessor(cookie)

opener = urllib2.build_opener(cookieHandler)

request = urllib2.Request("http://www.baidu.com")

response = opener.open(request)

cookie.save(ignore_discard=True,ignore_expires=True)
# for item in cookie:
#     print "Name:"+item.name
#     print "Value:"+item.value
