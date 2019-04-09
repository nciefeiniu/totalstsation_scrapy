# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from .models import session, PageInfo
from sqlalchemy import exists


class TotalstationSpiderPipeline(object):
    def __init__(self):
        self.session = session

    def process_item(self, item, spider):
        try:
            if 'gov.cn' not in item['currenturl']:
                return
            existence = self.session.query(
                exists().where(PageInfo.contentmd5==item['contentmd5'])
            ).scalar()
            if not existence:
                # 不存在
                self.session.add(
                    PageInfo(baseurl=item['baseurl'], currenturl=item['currenturl'], content=item['content'], fetchtime=item['fetchtime'],
                             contentmd5=item['contentmd5'], contenttype=item['contenttype'], prevfetchtime=item['prevfetchtime'],
                             domain_name=item['domain_name'], page_title=item['page_title']))
            else:
                # 数据存在，更新操作
                self.session.query(PageInfo).filter(PageInfo.contentmd5 == item['contentmd5']).update(
                    {'content': item['content'], 'contentmd5': item['contentmd5'], 'contenttype': item['contenttype'],
                     'page_title': item['page_title'], 'fetchtime': item['fetchtime']
                     }
                )
            self.session.commit()
        except Exception as e:
            print(e)
            self.session.rollback()
        return item

    def __del__(self):
        self.session.close()
