# 大众点评美食频道的爬虫

---
## 此项目包含俩个爬虫(shopinfo,dianping):
### shopinfo爬虫用于获取店铺的信息与id
`scrapy crawl shopinfo`
### dianping爬虫用于获取店铺下的所有评论信息
`scrapy crawl dianping`

---
## 数据库与存储:

 数据库采用sqlalachemy+mysql进行存储

---
## Settings设置:
`LOG_LEVEL ='INFO'`表示只显示INFO等级以上的信息

`JOBDIR = 'pause'` 表示开启中断续爬功能，并将状态存储于pause文件夹中

---
## MiddleWares:
添加了UserAgentmiddleware与Cookiesmiddleware来获取随机的header与cookies

## 配置重爬:
在爬虫完成后，删除pause文件夹，也就是删除了之前保存的运行状态，重新运行爬虫即可开始重爬.重爬依然是遍历url，获取每个url内的数据信息，在存储进数据库前进行判断
，根据某个字段的内容是否在数据库已经存在了来决定是否将此条数据存入数据库.我选择的是modified_at(评论最后一次修改时间)字段，这样如果同一条评论信息被评论人修改
了内容，modified_at一定会发生变化，这样就可以同时保存新旧俩个版本。当然也可以通过post_at字段来判定，这样如果同一条信息内容被修改，但是post_at(评论发布时间)
不会发生变化，这样就可以让新版本覆盖旧版本了.
