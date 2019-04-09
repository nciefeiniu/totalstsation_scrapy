#!/usr/bin/env python 
# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from fake_useragent import UserAgent
import hashlib

# 默认的lua_script
default_script = """
function main(splash, args)
  splash:runjs("Object.defineProperty(navigator,'platform',{get:function(){return 'Windows';}});")
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })
  assert(splash:wait(2))
  splash.scroll_position = {x=0, y=20000}
  return splash:html()
end
"""


# 修改的链接过滤器，需要增加一个参数baseurl
def default_process_link(links, baseurl):
    _base_domain = urlparse(baseurl).netloc
    _links = []
    for link in links:
        if urlparse(link.url).netloc == _base_domain:
            _links.append(link)
    return _links


def js_click_function(jsfunc):
    # 支持点击事件的lua_script，点击时间需要通过args传递参数类型!!!
    # 可以使用jquery的方法，lua会导入jquery代码
    click_script = """
    function main(splash, args)
      splash:runjs("Object.defineProperty(navigator,'platform',{{get:function(){{return 'Windows';}}}});")
      ok, reason = splash:autoload("https://code.jquery.com/jquery-2.1.3.min.js")
      assert(splash:go(args.url))
      assert(splash:wait(args.wait))
      splash.scroll_position = {{x=0, y=20000}}
      local click_a = splash:jsfunc([[
        function() {{
            try{{
                {0}
            }}catch(err){{
            
            }}
        }}
      ]])
      
      click_a()
      splash:wait(args.wait)
      return splash:html()
    end
    """.format(jsfunc)
    return click_script


def get_headers():
    ua = UserAgent(verify_ssl=False)
    return {'User-Agent': ua.random, 'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}


def get_md5(datas: bytes):
    m = hashlib.md5()
    m.update(datas)
    return m.hexdigest()


if __name__ == "__main__":
    # print(get_headers())
    _ai = 2
    res = js_click_function("""$("a[href^='#']")[{0}].click();""".format(_ai))
    print(res)
