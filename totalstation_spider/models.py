#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Tao Liu'

import os
from datetime import datetime

# 外键关联
# 创建实例，并连接数据库
from dotenv import find_dotenv, load_dotenv
# 导入要使用的字段类型
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import create_engine, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())
envget = os.environ.get
dbuser = envget('PSQL_USER')  # "dbuser"
dbpassword = envget('PSQL_PASSWORD')  # ,"123456"
dbhost = envget('PSQL_HOST')  # ,"192.168.1.156"
dbport = envget('PSQL_PORT')  # ,"5433"
dbname = envget('PSQL_DATABASE')
# echo=True 显示信息
print('postgresql+psycopg2://%s:%s@%s:%s/%s' % (dbuser, dbpassword, dbhost, dbport, dbname))
engine = create_engine('postgresql+psycopg2://%s:%s@%s:%s/%s' % (dbuser, dbpassword, dbhost, dbport, dbname),
                       echo=False)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()  # 生成orm基类


class PageInfo(Base):
    __tablename__ = 'webpageinfo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    baseurl = Column(String)  # 基础url
    currenturl = Column(String)  # 当前的url
    prevfetchtime = Column(DateTime)  # 上次下载时间
    fetchtime = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 下载时间
    content = Column(Text)  # 内容
    contentmd5 = Column(String)  # 内容的md5值
    contenttype = Column(String)  # 内容的类型
    domain_name = Column(String)  # 域名
    page_title = Column(String)  # 页面的title信息

    __table_args__ = (
        UniqueConstraint('currenturl', 'contentmd5'),  # 唯一索引
    )


def init_db():
    Base.metadata.create_all(engine)  # 创建表结构 （这里是父类调子类）


def drop_db():
    Base.metadata.drop_all(engine)


# 初始化数据库
if __name__ == '__main__':
    # drop_db()
    init_db()
