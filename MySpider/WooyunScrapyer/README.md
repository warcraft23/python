# 基于Scrapy爬虫框架的Wooyun漏洞信息抓取爬虫
## 目的
抓取Wooyun上公开的漏洞信息，将信息在本地持久化，以备将来查阅。

## 持久化方式
sqlite3进行一些漏洞基本信息的存储，其中有个contentpath域用于存储详情文件的路径。

详情文件比较庞大，因此采用在Content文件夹下的文本进行存储。

## 使用方法
安装Scrapy之后在WooyunScrapyer文件夹下执行 

~~~bash
scrapy crawl wooyunScrapyer -a roundnum=74
~~~

这里的`roundnum`参数用于表示要抓取的目录页 页数/1，因此以上的74代表740个页面。
