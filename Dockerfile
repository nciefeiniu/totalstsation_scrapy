# 分布式爬虫
FROM python:3.5

MAINTAINER <Tao Liu>


COPY sources.list /etc/apt/sources.list

COPY pip.conf /root/.pip/pip.conf

COPY ./ /data/scrapy/total_spider

WORKDIR /data/scrapy/total_spider

# 环境变量
RUN cp ./.env_sample ./totalstation_spider/.env

RUN apt update && pip3 install -r requirements.txt

# 修改时间
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 运行爬虫
CMD ["scrapy", "crawl", "totalspider"]