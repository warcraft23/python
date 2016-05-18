# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 这个是我的爬虫将数据爬取之后再存储到我的数据库中的管道
# 用于将爬虫获取到的item中的数据提取并存入数据库之中
# 需要做的仅仅是SQL语句的插入操作，就是insert咯，我先试试哈

import mysql.connector
import sqlite3
import os
import sys

WooyunScrapyerWorkdir = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)
DBFILENAME = os.path.join(WooyunScrapyerWorkdir, "db/WooyunBugs.db")

CreateWooyunBugsTableSql = '''CREATE TABLE IF NOT EXISTS `BugDetail` (
`id` INTEGER PRIMARY KEY AUTOINCREMENT,
`bugindex` varchar(1024),
`title` varchar(1024),
`corp` varchar(256),
`author` varchar(256),
`submit_date` varchar(256),
`open_date` varchar(256),
`type` varchar(256),
`level` varchar(64),
`myrank` varchar(256),
`status` varchar(256),
`tags` varchar(10240)
)'''

CreateWooyunBugsIndexSql = "create index BugDetail_index on BugDetail(bugindex,title,type)"

sql_insert = '''INSERT INTO
BugDetail(bugindex,title,corp,author,submit_date,open_date,type,level,myrank,status,tags)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

def tableExist(tbname):
    if not os.path.exists(DBFILENAME):
        print "table[%s] doesn't exist" %(tbname)
        return False
    else:
        sqlstr = "select count(*) from sqlite_master where type='table' and name='%s'" %(tbname)
        conn = sqlite3.connect(DBFILENAME)
        cu = conn.cursor()
        cu.execute(sqlstr)
        r = cu.fetchall()
        cu.close()
        conn.close()
        if r[0][0] == 1:
            return True
        else:
            print "table[%s] doesn't exist" %(tbname)
            return False

def create_table(tbname, crttblsql, crtindexsql):
    if tableExist(tbname) is False:
        conn = sqlite3.connect(DBFILENAME)
        cu = conn.cursor()
        cu.execute(crttblsql)
        conn.commit()
        cu.execute(crtindexsql)
        conn.commit()
        cu.close()
        conn.close()

def excuteSelSql(conn,sql):
    if sql is not None and sql !='':
        cu = conn.cursor()
        cu.execute(sql)
        r = cu.fetchall()
        cu.close()
        if len(r) > 0:
            return r
        else:
            return None

def excutesqlstr(conn, sql):
    if sql is not None and sql != '':
        cu = conn.cursor()
        cu.execute(sql)
        conn.commit()
        cu.close

def excuteInsUpdDelSql(conn, sql, data):
    if sql is not None and sql != '':
        if data is not None:
            cu = conn.cursor()
            for d in data:
                cu.execute(sql,d)
                conn.commit()
            cu.close()


class WooyunscrapyerPipeline(object):
    def open_spider(self, spider):
        create_table("BugDetail", CreateWooyunBugsTableSql, CreateWooyunBugsIndexSql)
        # self.conn = mysql.connector.connect(host='localhost', user='Edward', passwd='123', db='BugsInWooyun')
        # self.cursor = self.conn.cursor()
        self.conn = sqlite3.connect(DBFILENAME,check_same_thread=False)
        self.conn.text_factory = str
        # self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()
        # self.conn.close()

    def process_item(self, item, spider):
        tags = ''
        if item['wybug_tags']:
            for str in item['wybug_tags']:
                tags += str + ' '
        else:
            tags = '无'
        data = (item['wybug_index'][0], item['wybug_title'][0], item['wybug_corp'][0],
                item['wybug_author'][0], item['wybug_submit_date'][0], item['wybug_open_date'][0], item['wybug_type'][0],
                item['wybug_level'][0], item['wybug_myrank'][0], item['wybug_status'][0], tags)
        newdata = []
        newdata.append(data)
        print "======================================"
        # print newdata[0][0]
        checkstr = "select bugindex,title,corp,author,submit_date,open_date," \
                   "type,level,myrank,status,tags from BugDetail where bugindex='%s'" % (newdata[0][0])
        # print checkstr
        olddata = excuteSelSql(self.conn, checkstr)
        if olddata is None:
            excuteInsUpdDelSql(self.conn, sql_insert, newdata)
        else:
            if cmp(olddata, newdata) != 0:
                UpdateBugInfoSql = "update BugDetail " \
                                   "set title='%s',corp='%s',author='%s',submit_date='%s',open_date='%s'," \
                                   "type='%s',level='%s',myrank='%s',status='%s',tags='%s' where bugindex='%s'" % (
                    newdata[0][1], newdata[0][2], newdata[0][3], newdata[0][4], newdata[0][5], newdata[0][6],
                    newdata[0][7], newdata[0][8], newdata[0][9], newdata[0][10], newdata[0][0]
                )
                excutesqlstr(self.conn, UpdateBugInfoSql)

        return item
