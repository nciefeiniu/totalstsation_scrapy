#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import re
from scrapy.http import HtmlResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy_splash import SplashJsonResponse, SplashTextResponse, SplashResponse
from scrapy_splash import SplashRequest, SplashMiddleware
from bs4 import BeautifulSoup as BS

from ..utils import default_process_link, default_script, get_headers, js_click_function


# CLICK_HREF = re.compile(r'(^javascript)|(^#)')


class TotalStationSpider(RedisCrawlSpider):
    name = 'ts_spider'

    redis_key = 'waiting_for_crawl:start_urls'

    # rules 抓取所有链接， process_links为过滤器
    rules = (
        Rule(link_extractor=LinkExtractor(), process_links=default_process_link, callback='parse_m', follow=True),
    )

    # 重写父类的start_requests方法，修改为用SplashRequest发起请求
    def start_requests(self):
        for url in self.start_urls:
            headers = get_headers()
            yield SplashRequest(url=url, callback=self.parse_m, endpoint='execute', dont_filter=True, headers=headers,
                                resource_timeout=60,
                                args={'url': url, 'wait': 5, 'lua_source': default_script},
                                )

    # 重写CrawlSpider 的这个方法
    def _requests_to_follow(self, response):
        if not isinstance(response, (HtmlResponse, SplashJsonResponse, SplashTextResponse, SplashResponse)):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                # 修改process_links方法，增加一个参数 response.url，用来作为过滤条件
                links = rule.process_links(links, response.url)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)

    def _build_request(self, rule, link):
        # 重要！！！！！这里重写父类方法，特别注意，需要传递meta={'rule': rule, 'link_text': link.text}
        # 详细可以查看 CrawlSpider 的源码
        headers = get_headers()
        r = SplashRequest(url=link.url, callback=self._response_downloaded, meta={'rule': rule, 'link_text': link.text},
                          args={'wait': 5, 'url': link.url, 'lua_source': default_script}, headers=headers)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    def _re_request(self, url, jsfunc: str = None, document_num=0):
        # 需要再次请求的方法，可选是否增加点击事件
        headers = get_headers()
        # TODO 携带点击事件的再次请求
        yield SplashRequest(url=url, callback=self.parse, endpoint='execute', dont_filter=True, headers=headers,
                            resource_timeout=60,
                            args={'url': url, 'wait': 5, 'lua_source': js_click_function(jsfunc)})

    def parse_m(self, response):
        # 找出需要点击的地方
        soup = BS(response.text, 'lxml')
        # print(response.text)
        href_null = soup.find_all('a', href=re.compile(r'^javascript'))
        href_sharp = soup.find_all('a', href=re.compile(r'^#'))
        print(len(href_sharp), len(href_null))

        # TODO 找出需要点击的地方，再次请求并点击
        # yield self._re_request(response.url)
        for _i in range(len(href_null)):
            _jsfunc = """$("a[href^='javascript']")[{0}].click();""".format(_i)
            print(_jsfunc)
            self._re_request(response.url, _jsfunc)
        for _i in range(len(href_sharp)):
            _jsfunc = """$("a[href^='#']")[{0}].click();""".format(_i)
            self._re_request(response.url, _jsfunc)

        # TODO 保存当前页面的信息, items
        print(response.url)
