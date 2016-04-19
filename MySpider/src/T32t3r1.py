# coding=utf-8
import types

__author__ = 'Edward'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import urllib2
import re

def getBugDetail(url):
    request =urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        print e.code
    except urllib2.URLError, e:
        print e.reason


    # print respone.read()
    pattern = re.compile(r'[\s\t\n]')
    detailStr = re.sub(pattern, '', response.read())
    # print detailStr

    pattern = re.compile(r'缺陷编号：([^\s]+)<!--BaiduButtonBEGIN-->')

    result = re.search(pattern, detailStr)

    mytuple = []
    if result:
        # print result.group()
        mydict = {}

        myPattern = re.compile(r'WooYun-2015-(\d*)')
        index = re.search(myPattern, result.group()).group()
        # print index
        mydict[u'缺陷编号']= index


        myPattern = re.compile(r'漏洞标题：(.+)</h3><h3class=\'wybug_corp\'>')
        title = re.search(myPattern, result.group()).group()
        myPattern = re.compile(r'漏洞标题：')
        title = re.sub(myPattern,'',title)
        myPattern = re.compile(r'</h3><h3class=\'wybug_corp\'>')
        title = re.sub(myPattern,'',title)
        # print title
        mydict[u'漏洞标题']= title

        myPattern = re.compile(ur'相关厂商：<ahref=\"http://www\.wooyun\.org/corps/(.+?)>')
        corp = re.search(myPattern, result.group().decode('utf-8')).group(1)
        # myPattern = re.compile(ur'相关厂商：<ahref=\"http://www\.wooyun\.org/corps/')
        # corp = re.sub(myPattern, '', corp)
        mydict[u'相关厂商']= corp

        myPattern = re.compile(ur'whitehats/(.+?)">')
        author = re.search(myPattern, result.group().decode('utf-8')).group(1)
        myPattern = re.compile(ur'whitehats/')
        author = re.sub(myPattern, '', author)
        mydict[u'漏洞作者']= author

        myPattern = re.compile(ur'提交时间：[:\-\d]+')
        time = re.search(myPattern, result.group().decode('utf-8')).group()
        myPattern = re.compile(ur'提交时间：')
        time = re.sub(myPattern, '', time)
        mydict[u'提交时间']= time

        myPattern = re.compile(ur'公开时间：[:\-\d]+')
        time = re.search(myPattern, result.group().decode('utf-8')).group()
        myPattern = re.compile(ur'公开时间：')
        time = re.sub(myPattern, '', time)
        mydict[u'公开时间']= time

        myPattern = re.compile(ur'漏洞类型：[\u4E00-\u9FA5\w]+')
        type = re.search(myPattern, result.group().decode('utf-8')).group()
        myPattern = re.compile(ur'漏洞类型：')
        type = re.sub(myPattern, '', type)
        mydict[u'漏洞类型']= type

        myPattern = re.compile(ur'危害等级：[\u4E00-\u9FA5]')
        level = re.search(myPattern, result.group().decode('utf-8')).group()
        myPattern = re.compile(ur'危害等级：')
        level = re.sub(myPattern, '', level)
        mydict[u'危害等级']= level

        myPattern = re.compile(ur'自评Rank：\d+')
        my_rank = re.search(myPattern, result.group().decode('utf-8')).group()
        myPattern = re.compile(ur'自评Rank：')
        my_rank = re.sub(myPattern, '', my_rank)
        mydict[u'自评Rank']= my_rank

        myPattern = re.compile(ur'漏洞状态：[\u4E00-\u9FA5]+')
        status = re.search(myPattern, result.group().decode('utf-8')).group()
        myPattern = re.compile(ur'漏洞状态：')
        status = re.sub(myPattern, '', status)
        mydict[u'漏洞状态']= status


        myPattern = re.compile(r'<ahref="/tags/.+?">(.*?)</a>')
        bug_tags = []
        if len(re.findall(myPattern, result.group().decode('utf-8'))):
            tags = re.findall(myPattern, result.group().decode('utf-8'))
            for tag in tags:
                # print tag
                bug_tags.append(tag)
        else:
            tag = '无'
            bug_tags.append(tag)
        mydict[u'漏洞标签']= bug_tags


        for item in mydict:
            print item + ':',
            if isinstance(mydict[item], types.ListType):
                for i in mydict[item]:
                    print i + " ",
                print
            else:
                print mydict[item]





def getWooyunBugsPage():
    index = 2
    end = index+1
    while True:
        if index == end:
            break
        else:
            print index
            print "======================================"
            url_base = "http://www.wooyun.org/bugs/new_public/page/"
            url = url_base + str(index)
            index += 1
            request = urllib2.Request(url)

            try:
                response = urllib2.urlopen(request)
            except urllib2.HTTPError, e:
                print e.code
            except urllib2.URLError, e:
                print e.reason
            # print response.read()

            # 读取其中缺陷编号位2015的漏洞
            pattern = re.compile(r'a href="/bugs/wooyun-2015-(\d+)"')
            # if len(re.findall(pattern, response.read())):
            result = re.findall(pattern, response.read())
            for item in result:
                bugURL = "http://www.wooyun.org/bugs/wooyun-2015-" + item
                print "Start Capture Link:  " + bugURL
                getBugDetail(bugURL)
                print "======================================"



def main():
    getWooyunBugsPage()
    # print "Hello World!"

main()
