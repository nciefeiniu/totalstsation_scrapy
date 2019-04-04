#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from scrapy_splash import SplashRequest
from ..utils import SplashRedisCrawlSpider
from ..utils import default_script


class TSpider(SplashRedisCrawlSpider):
    name = 'tspider'

    # 重写父类的start_requests方法，修改为用SplashRequest发起请求
    def start_requests(self):
        for url in self.start_urls:
            if 'gov.cn' in url:
                # headers = get_headers()
                yield SplashRequest(url=url, callback=self.parse_m, endpoint='execute', dont_filter=True,
                                    args={'url': url, 'wait': 5, 'lua_source': default_script}
                                    )