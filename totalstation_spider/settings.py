# -*- coding: utf-8 -*-

import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
envget = os.environ.get

# Scrapy settings for totalstation_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'totalstation_spider'

SPIDER_MODULES = ['totalstation_spider.spiders']
NEWSPIDER_MODULE = 'totalstation_spider.spiders'

# scrapy_redis调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 广度优先
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'

SCHEDULER_PERSIST = True

# scrapy_redis去重
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# SCRAPY-REDIS使用得redis地址
REDIS_URL = envget('REDIS_URL')

# 使用Splash的Http缓存
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# splash url
SPLASH_URL = envget('SPLASH_URL')

FEED_EXPORT_ENCODING = 'utf-8'

# 广度优先
DEPTH_PRIORITY = int(envget('DEPTH_PRIORITY'))

# DNS 缓存
DNSCACHE_ENABLED = True

# 进程所有的标准输出(及错误)将会被重定向到 log 中
LOG_STDOUT = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'totalstation_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = int(envget('CONCURRENT_REQUESTS'))

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = int(envget('DOWNLOAD_DELAY')if envget('DOWNLOAD_DELAY') else 0)
# The download delay setting will honor only one of:
# 对单个网站得并发数
# CONCURRENT_REQUESTS_PER_DOMAIN = int(envget('CONCURRENT_REQUESTS_PER_DOMAIN') if envget('CONCURRENT_REQUESTS_PER_DOMAIN') else 0)
# 对单个Ip得最大并发
# CONCURRENT_REQUESTS_PER_IP = int(envget('CONCURRENT_REQUESTS_PER_IP') if envget('CONCURRENT_REQUESTS_PER_IP') else 0)

# Disable cookies (enabled by default)
COOKIES_ENABLED = True

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'totalstation_spider.middlewares.TotalstationSpiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'totalstation_spider.middlewares.RandomUserAgentMiddleware': 543,
    'totalstation_spider.middlewares.LocalRetryMiddleware': 500,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': None
}


# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'totalstation_spider.pipelines.TotalstationSpiderPipeline': 300,
}

# 重试次数
RETRY_TIMES = int(envget('RETRY_TIMES')) if envget('RETRY_TIMES') else 0

# 代理服务器
PROXY_SERVER = envget('PROXY')

# 自动限速
AUTOTHROTTLE_ENABLED = True

# 初始下载延迟
AUTOTHROTTLE_START_DELAY = int(envget('AUTOTHROTTLE_START_DELAY'))

# 高延迟下的最大下载延迟时间
AUTOTHROTTLE_MAX_DELAY = int(envget('AUTOTHROTTLE_MAX_DELAY'))

# 日志等级和日志目录
LOG_LEVEL = 'DEBUG'
LOG_FILE = 'scrapy.log'

