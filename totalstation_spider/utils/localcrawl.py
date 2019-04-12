#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import six

from scrapy.http import HtmlResponse
from scrapy.utils.spider import iterate_spider_output
from scrapy.spiders import Spider

from scrapy_splash import SplashJsonResponse, SplashTextResponse, SplashResponse
from scrapy_splash import SplashRequest

from ..utils import get_headers
from ..utils import default_script


def identity(x):
    return x


class Rule(object):

    def __init__(self, link_extractor, callback=None, cb_kwargs=None, follow=None, process_links=None, process_request=identity):
        self.link_extractor = link_extractor
        self.callback = callback
        self.cb_kwargs = cb_kwargs or {}
        self.process_links = process_links
        self.process_request = process_request
        if follow is None:
            self.follow = False if callback else True
        else:
            self.follow = follow


class LocalCrawlSpider(Spider):

    rules = ()

    def __init__(self, *a, **kw):
        super(LocalCrawlSpider, self).__init__(*a, **kw)
        self._compile_rules()

    def parse(self, response):
        return self._parse_response(response, self.parse_start_url, cb_kwargs={}, follow=True)

    def parse_start_url(self, response):
        return []

    def process_results(self, response, results):
        return results

    def _build_request(self, rule, link):
        # 重要！！！！！这里重写父类方法，特别注意，需要传递meta={'rule': rule, 'link_text': link.text}
        # 详细可以查看 CrawlSpider 的源码

        headers = get_headers()
        meta = {'rule': rule, 'link_text': link.text}
        # TODO args 考虑是否需要修改，这里的wait是否需要根据环境变量来获取
        args = {'wait': 5, 'url': link.url, 'lua_source': default_script}
        r = SplashRequest(url=link.url, callback=self._response_downloaded, meta=meta, splash_headers=headers,
                          endpoint='execute', headers=headers, args=args)
        r.meta.update(rule=rule, link_text=link.text)
        return r

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

    def _response_downloaded(self, response):
        rule = self._rules[response.meta['rule']]
        return self._parse_response(response, rule.callback, rule.cb_kwargs, rule.follow)

    def _parse_response(self, response, callback, cb_kwargs, follow=True):
        if callback:
            cb_res = callback(response, **cb_kwargs) or ()
            cb_res = self.process_results(response, cb_res)
            for requests_or_item in iterate_spider_output(cb_res):
                yield requests_or_item

        if follow and self._follow_links:
            for request_or_item in self._requests_to_follow(response):
                yield request_or_item

    def _compile_rules(self):
        def get_method(method):
            if callable(method):
                return method
            elif isinstance(method, six.string_types):
                return getattr(self, method, None)

        self._rules = [copy.copy(r) for r in self.rules]
        for rule in self._rules:
            rule.callback = get_method(rule.callback)
            rule.process_links = get_method(rule.process_links)
            rule.process_request = get_method(rule.process_request)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(LocalCrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
        spider._follow_links = crawler.settings.getbool(
            'CRAWLSPIDER_FOLLOW_LINKS', True)
        return spider

    def set_crawler(self, crawler):
        super(LocalCrawlSpider, self).set_crawler(crawler)
        self._follow_links = crawler.settings.getbool('CRAWLSPIDER_FOLLOW_LINKS', True)
