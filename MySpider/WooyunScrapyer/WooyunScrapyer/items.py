# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Bug(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    wybug_index         = scrapy.Field()
    wybug_title         = scrapy.Field()
    wybug_corp          = scrapy.Field()
    wybug_author        = scrapy.Field()
    wybug_submit_date   = scrapy.Field()
    wybug_open_date     = scrapy.Field()
    wybug_type          = scrapy.Field()
    wybug_level         = scrapy.Field()
    wybug_myrank        = scrapy.Field()
    wybug_status        = scrapy.Field()
    wybug_source        = scrapy.Field()
    wybug_tags          = scrapy.Field()
