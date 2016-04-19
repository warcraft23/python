# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 这个是我的爬虫将数据爬取之后再存储到我的数据库中的管道
# 用于将爬虫获取到的item中的数据提取并存入数据库之中
# 需要做的仅仅是SQL语句的插入操作，就是insert咯，我先试试哈

import mysql.connector

class WooyunscrapyerPipeline(object):
    def open_spider(self, spider):
        self.conn = mysql.connector.connect(host='localhost', user='Edward', passwd='123', db='BugsInWooyun')
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        sql_insert = 'INSERT INTO BugDetail(bug_id,title,corp,author,submit_date,open_date,type,level,myrank,status,tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        tags = ''
        if item['wybug_tags']:
            for str in item['wybug_tags']:
                tags += str + ' '
        else:
            tags = '无'
        data = (item['wybug_index'][0], item['wybug_title'][0], item['wybug_corp'][0], item['wybug_author'][0], item['wybug_submit_date'][0], item['wybug_open_date'][0], item['wybug_type'][0], item['wybug_level'][0], item['wybug_myrank'][0], item['wybug_status'][0], tags)
        try:
            self.cursor.execute(sql_insert, data)
            self.conn.commit()
        except:
            pass

        return item
