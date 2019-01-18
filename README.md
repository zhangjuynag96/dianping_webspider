# 大众点评美食频道的爬虫

---
## 此项目包含俩个爬虫(shopinfo,dianping):
### shopinfo爬虫用于获取店铺的信息与id
`scrapy crawl shopinfo`
### dianping爬虫用于获取店铺下的所有评论信息
`scrapy crawl dianping`

---
### 数据库方面采用sqlalachemy+mysql进行存储

---
### settings设置:
`LOG_LEVEL ='INFO'`表示只显示INFO等级以上的信息

`JOBDIR = 'pause'` 表示开启中断续爬功能，并将状态存储于pause文件夹中

---
### 添加了UserAgentmiddleware与Cookiesmiddleware来获取随机的header与cookies