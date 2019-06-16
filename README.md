## 网站通用爬虫 scrapy-splash and scrapy-redis


主要框架：
 
 - scrapy
 - scrapy-splash
 - scrapy-redis
 
 
`splash` 可以采用负载均衡，多节点部署。

`scrapy` 爬虫也需要多节点部署。单机全站爬取太慢。

---


#### splash 安装

[安装教程](https://github.com/scrapy-plugins/scrapy-splash#installation) 官方文档


---

#### 数据表结构
表结构在项目下的models.py中

```bash
python3 models.py
```

---


#### 测试环境下的分布式splash

 
宿主机安装 `nginx` 

```bash
apt install nginx -y
# or
yum install nginx -y
```

启动splash 容器

```bash
sudo ./create_splash.sh
```

修改 nginx 的配置文件(/etc/nginx/nginx.conf)，在 **http** 中增加

    upstream splash {
        least_conn;
        server 127.0.0.1:8051;
        server 127.0.0.1:8052;
        server 127.0.0.1:8053;
        server 127.0.0.1:8054;
        server 127.0.0.1:8055;
    }
    server {
        listen 8050;
        location / {
            proxy_pass http://splash;
            proxy_connect_timeout 300;
            proxy_read_timeout 400;
        }
    }


重新加载 nginx 配置文件

```bash
nginx -s reload
```

---


#### 测试环境下docker启动爬虫

```bash
git clone http://git.epmap.org/tao.liu/totalstation_spider.git

cd totalstation_spider
```

请修改 `.env_sample 文件`

```bash
# 编译镜像
docker build -t totalspider:v1 .

# 启动docker容器
docker run -itd --name xxx totalspider:v1
```

然后向redis 中添加代爬取的网站，
```bash
# 连接redis
redis-cli -h xx.xx.xx.xx -p xxxx

# 向redis中添加数据
lpush waiting_for_crawl:start_urls http://www.gov.cn
```

爬虫已经开始全站爬取。