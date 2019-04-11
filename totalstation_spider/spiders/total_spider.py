#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 这个才是最新版！！！不用ts_spider

import re
import sys

from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup as BS
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy_splash import SplashRequest

from ..utils import SplashRedisCrawlSpider
from ..utils import default_process_link, default_script, js_click_function
from ..utils import get_md5

# 修改递归上限
sys.setrecursionlimit(100000)


class TotalSpider(SplashRedisCrawlSpider):
    name = 'totalspider'

    redis_key = 'waiting_for_crawl:start_urls'

    # rules 抓取所有链接， process_links为过滤器
    rules = (
        Rule(link_extractor=LinkExtractor(), process_links=default_process_link, callback='parse_m', follow=True),
    )

    # 重写父类的start_requests方法，修改为用SplashRequest发起请求
    def start_requests(self):
        """Returns a batch of start requests from redis."""
        return self.next_requests()

    def make_requests_from_url(self, url):
        """ This method is deprecated. """
        return SplashRequest(url=url, callback=self.parse_m, endpoint='execute', dont_filter=True,
                             args={'url': url, 'wait': 5, 'lua_source': default_script}
                             )

    def _re_request(self, url, jsfunc=None, all_a=None):
        # 需要再次请求的方法，可选是否增加点击事件
        # _headers = get_headers().update({'Referer': url})
        # 携带点击事件的再次请求，meta增加baseurl，防止点击事件跳转到其他域名,meta中增加click标签，解析有这个就不再执行模拟点击！
        return SplashRequest(url=url, callback=self.parse_click, endpoint='execute', dont_filter=True,
                             args={'url': url, 'wait': 5, 'lua_source': js_click_function(jsfunc)},
                              meta={'baseurl': url, 'click': True}
                             )

    def _re_request_next_page(self, url, md_5: str, script: str=None):
        # 点击下一页的请求，请求中携带当前页面的md5值，之后好根据这个判断是否还有下一页
        # _headers = get_headers().update({'Referer': url})
        return SplashRequest(url=url, callback=self.parse_nextpage, endpoint='execute', dont_filter=True,
                             args={'url': url, 'wait': 5, 'lua_source': script},
                             meta={'nextpage': True, 'md5': md_5, 'jsfunc': script})

    # TODO 这个下一页的规则还要增加
    next_pattern_contain = re.compile(r'([下后]\s*一?\s*页\s*>*)|(\s?>{2}\s?)|(^\s*>+\s*$)')
    # ly_next_pattern_contain = re.compile(r'(\s?>{2}\s?)')
    # next_pattern_equal = re.compile(r'(^\s*>+\s*$)')

    def parse_m(self, response):
        # 这是不带点击的回调

        # 保存当前页面的信息, items
        yield self.save_info(response)

        # 找出需要点击的地方，这里会转换为jquery的方式在splash中运行
        soup = BS(response.text, 'lxml')
        a_javascript = soup.find_all('a', href=re.compile(r'^javascript'))
        a_sharp = soup.find_all('a', href=re.compile(r'^#'))
        _all_a = a_javascript + a_sharp
        for _i in range(len(a_javascript)):
            _jsfunc = """$("a[href^='javascript']")[{0}].click();""".format(_i)
            yield self._re_request(response.url, _jsfunc, _all_a)
        for _ai in range(len(a_sharp)):
            _jsfunc = """$("a[href^='#']")[{0}].click();""".format(_ai)
            yield self._re_request(response.url, _jsfunc, _all_a)

        # TODO 点击ajax请求的下一页，这里采用的选出所有a标签，再根据第几个标签是 下一页按钮   来转换为jquery能识别的代码，进行模拟点击。   还有其他好的方法？
        _nextpages_javascrpit = soup.find_all('a', href=re.compile('^javascript'))
        _nextpages_sharp = soup.find_all('a', href=re.compile('^#'))
        if _nextpages_javascrpit or _nextpages_sharp:
            for _i in range(len(_nextpages_javascrpit)):
                if not _nextpages_javascrpit[_i].find(text=self.next_pattern_contain):
                    continue
                _script = """$("a[href^='javascript']")[{0}].click();""".format(_i)
                yield self._re_request_next_page(response.url, md_5=get_md5(response.body), script=_script)
            for _i in range(len(_nextpages_sharp)):
                if not _nextpages_sharp[_i].find(text=self.next_pattern_contain):
                    continue
                _script = """$("a[href^='#']")[{0}].click();""".format(_i)
                yield self._re_request_next_page(response.url, md_5=get_md5(response.body), script=_script)

    def parse_click(self, response):
        # 判断是否跳转到了新域名，跳转到了新域名，抛弃，不要
        if urlparse(response.url).netloc != urlparse(response.meta['baseurl']).netloc:
            return

        # 保存当前页面的信息, items
        # yield self.save_info(response)

        # 这是带点击事件请求的回调
        _bae_url = response.meta['baseurl']
        if _bae_url == response.url:
            # 没有跳转到新页面，需要判断是否有下一页按钮

            # TODO 点击ajax请求的下一页
            _soup = BS(response.text, 'lxml')
            _nextpages_javascrpit = _soup.find_all('a', href=re.compile('^javascript'))
            _nextpages_sharp = _soup.find_all('a', href=re.compile('^#'))
            if _nextpages_javascrpit or _nextpages_sharp:
                for _i in range(len(_nextpages_javascrpit)):
                    if not _nextpages_javascrpit[_i].find(text=self.next_pattern_contain):
                        continue
                    _script = """$("a[href^='javascript']")[{0}].click();""".format(_i)
                    yield self._re_request_next_page(response.url, md_5=get_md5(response.body), script=_script)
                for _i in range(len(_nextpages_sharp)):
                    if not _nextpages_sharp[_i].find(text=self.next_pattern_contain):
                        continue
                    _script = """$("a[href^='#']")[{0}].click();""".format(_i)
                    yield self._re_request_next_page(response.url, md_5=get_md5(response.body), script=_script)
        else:
            pass
            # TODO 跳转到了新页面(还需考虑这个页面是否市政府或者环保部的页面，是否丢弃)，
            # TODO 考虑是否可以把这个url加入到redis中！直接再交给parse_m来处理，有可能造成递归栈溢出，还有什么好方法能解决这个问题?

    def parse_nextpage(self, response):
        # 点击下一页之后的回调
        if 'nextpage' not in response.meta:
            return

        if 'md5' not in response.meta:
            return

        if 'jsfunc' not in response.meta:
            return

        if get_md5(response.body) == response.meta['md5']:
            return

        # 保存信息
        # yield self.save_info(response)

        # 再次请求，点击下一页
        yield self._re_request_next_page(url=response.url, md_5=get_md5(response.body), script=response.meta['jsfunc'])

    def save_info(self, response, click=False):

        from ..items import TotalstationSpiderItem

        _items = TotalstationSpiderItem()
        _items['baseurl'] = response.meta['baseurl'] if 'baseurl' in response.meta else response.url
        _items['currenturl'] = response.url
        _items['prevfetchtime'] = datetime.now()
        _items['fetchtime'] = datetime.now()

        # TODO 需要根据返回类型判断怎么存储
        _items['contenttype'] = response.headers.get('Content-Type').decode(response.encoding)

        _items['content'] = response.text

        _items['contentmd5'] = get_md5(response.body)

        _items['domain_name'] = urlparse(response.url).netloc

        _items['page_title'] = response.xpath('//title//text()').get() if response.xpath('//title//text()') else ''

        _items['page_body'] = response.xpath('//body').get() if response.xpath('//body') else ''

        return _items
