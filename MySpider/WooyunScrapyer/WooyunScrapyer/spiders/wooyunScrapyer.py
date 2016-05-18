# -*- coding: utf-8 -*-
import threading
import urllib2
import re

import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector

import sys
sys.path.append('..')
reload(sys)
sys.setdefaultencoding("utf-8")
from WooyunScrapyer.items import Bug

class WooyunscrapyerSpider(scrapy.Spider):
    name = "wooyunScrapyer"
    allowed_domains = ["http://www.wooyun.org"]
    start_urls = []

    def __init__(self, roundnum=None,*args,**kwargs):
        self.roundnum = int(roundnum)
        super(WooyunscrapyerSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        threadpool = []
        for i in range(self.roundnum):
            start_index = 1+i*10
            end_index = (i+1)*10
            th = threading.Thread(target=self.get_bug_URL, args=(start_index, end_index))
            threadpool.append(th)

        for th in threadpool:
            th.start()
        for th in threadpool:
            threading.Thread.join(th)

        # print self.start_urls
        start = ''
        while start is not 'y':
            print 'Shall We Start? y/n'
            start = raw_input()
            if start is 'n':
                exit()

        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def get_bug_URL(self, start, end):
        index = start
        while True:
            if index == end:
                break
            # print 'Crawling Page', index, 'OF Public Bugs'
            # print "======================================"
            url_base = "http://www.wooyun.org/bugs/new_public/page/"
            url = url_base + str(index)
            index += 1
            request = urllib2.Request(url, headers={
                                          "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36"
                                      })

            try:
                response = urllib2.urlopen(request)
            except urllib2.HTTPError, e:
                print e.code
            except urllib2.URLError, e:
                print e.reason

            # 读取其中漏洞
            pattern =re.compile(r'a href="/bugs/wooyun-(201\d-\d+)"')
            result = re.findall(pattern, response.read())
            if result:
                for item in result:
                    bugURL = "http://www.wooyun.org/bugs/wooyun-" + item
                    # print "Insert URL:", bugURL, "into start_urls"
                    self.start_urls.append(bugURL)
                    # print "======================================"
            else:
                # 如果当前页面不存在编号2015带头的漏洞，则结束抓取链接，进入抓取漏洞详情函数
                break

    def parse(self, response):
        sel = Selector(response)
        bug = Bug()

        #设置漏洞编号
        bug['wybug_index']      = sel.xpath('//div[@class="content"]/h3[1]/a/text()').extract()
        # for item in bug['wybug_index']:
        #     print '[', item, ']'

        #设置漏洞标题
        title                   = sel.xpath('//div[@class="content"]/h3[2]/text()').extract()[0]
        title                   = title.encode('utf-8')
        title                   = re.sub(r'[\s\r\n]', '', title)
        title                   = re.sub(r'漏洞标题：', '', title)
        bug['wybug_title']      = [title.decode('utf-8')]
        # for item in bug['wybug_title']:
        #     print item

        #设置漏洞厂商
        corp                    = sel.xpath('//div[@class="content"]/h3[3]/a/text()').extract()[0]
        corp                    = re.sub(r'[\s\r\n]', '', corp)
        bug['wybug_corp']       = [corp]
        # for item in bug['wybug_corp']:
        #     print item

        #设置漏洞作者
        bug['wybug_author']     = sel.xpath('//div[@class="content"]/h3[4]/a/text()').extract()
        # for item in bug['wybug_author']:
        #     print item

        #设置漏洞提交时间
        time                    = sel.xpath('//div[@class="content"]/h3[@class="wybug_date"]/text()').extract()[0]
        time                    = time.encode('utf-8')
        time                    = re.sub(r'[\r\n\t]', '', time)
        time                    = re.sub(r'提交时间：', '', time)
        bug['wybug_submit_date']= [time.decode('utf-8')]
        # for item in bug['wybug_submit_date']:
        #     print item

        #设置漏洞公开时间
        time                    = sel.xpath('//div[@class="content"]/h3[@class="wybug_open_date"]/text()').extract()[0]
        time                    = time.encode('utf-8')
        time                    = re.sub(r'[\r\n\t]', '', time)
        time                    = re.sub(r'公开时间：', '', time)
        bug['wybug_open_date']  = [time.decode('utf-8')]
        # # for item in bug['wybug_open_date']:
        #     print item

        #设置漏洞类型
        type                    = sel.xpath('//div[@class="content"]/h3[@class="wybug_type"]/text()').extract()[0]
        type                    = type.encode('utf-8')
        type                    = re.sub(r'[\t\r\s\n]', '', type)
        type                    = re.sub(r'漏洞类型：', '', type)
        bug['wybug_type']  = [type.decode('utf-8')]
        # for item in bug['wybug_type']:
        #     print item

        #设置危害等级
        level                   = sel.xpath('//div[@class="content"]/h3[@class="wybug_level"]/text()').extract()[0]
        level                   = level.encode('utf-8')
        level                   = re.sub(r'[\t\r\s\n]', '', level)
        level                   = re.sub(r'危害等级：', '', level)
        bug['wybug_level']      = [level.decode('utf-8')]
        # for item in bug['wybug_level']:
        #     print item

        #设置RANK
        myPattern               = re.compile(r'自评Rank：([\t\d]+)')
        rank                    = re.search(myPattern, response.body.encode('utf-8')).group()
        rank                    = re.sub(r'[\t\r\s\n]', '', rank)
        rank                    = re.sub(r'自评Rank：', '', rank)
        bug['wybug_myrank']     = [int(rank)]
        # for item in bug['wybug_myrank']:
        #     print item

        #设置漏洞状态
        status                  = sel.xpath('//div[@class="content"]/h3[@class="wybug_status"]/text()').extract()[0]
        status                  = status.encode('utf-8')
        status                  = re.sub(r'[\t\r\s\n]', '', status)
        status                  = re.sub(r'漏洞状态：', '', status)
        bug['wybug_status']     = [status.decode('utf-8')]
        # for item in bug['wybug_status']:
        #     print item

        #设置漏洞标签
        bug['wybug_tags']       = sel.xpath('//span[@class="tag"]/a/text()').extract()
        # for item in bug['wybug_tags']:
        #     print item

        # print '==================================================='

        return bug