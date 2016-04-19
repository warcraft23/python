# -*- coding: utf-8 -*-

import mysql.connector

conn = mysql.connector.connect(host='localhost', user='Edward', passwd='123', db='BugsInWooyun')

cursor = conn.cursor()

# 插入的数据格式为： %s是占位符不是格式化字符串
# bug_id(varchar) title(varchar) corp(varchar) author(varchar)
# submit_date(varchar) open_date(varchar) type(varchar)
# level(varchar) myrank(int) status(varchar) tags(varchar)
sql_insert = 'INSERT INTO BugDetail(bug_id,title,corp,author,submit_date,open_date,type,level,myrank,status,tags) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
data = ('WooYun-2015-000001', 'test', 'test', 'test', 'test', 'test', 'test', 'high', 10, 'test', 'test')


cursor.execute(sql_insert, data)

conn.commit()
# data = cursor.fetchall()

sql_select = 'select * from BugDetail'

cursor.execute(sql_select)

my_data = cursor.fetchall()

for item in my_data:
    print item

cursor.close()

conn.close()