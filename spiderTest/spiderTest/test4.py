#coding:utf_8
#HTTPError

import urllib2
request = urllib2.Request("http://www.csdn.com/cqcre")

try:
    urllib2.urlopen(request)
#except urllib2.HTTPError,e:
#    print e.code
except urllib2.URLError,e:
    if hasattr(e,"reason"):
        print e.reason
    if hasattr(e, "code"):
        print e.code
else:
    print "OK"