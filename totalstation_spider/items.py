# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TotalstationSpiderItem(scrapy.Item):

    baseurl = scrapy.Field()  # 基础url
    currenturl = scrapy.Field()  # 当前的url
    prevfetchtime = scrapy.Field()  # 上次下载时间
    fetchtime = scrapy.Field()  # 下载时间
    content = scrapy.Field()  # 内容
    contentmd5 = scrapy.Field()  # 内容的md5值
    contenttype = scrapy.Field()  # 内容的类型
    domain_name = scrapy.Field()  # 域名
    page_title = scrapy.Field()  # 页面的title
    page_body = scrapy.Field()  # 页面的body部分

