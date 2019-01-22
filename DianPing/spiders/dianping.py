# -*- coding: utf-8 -*-
import scrapy
import requests
from DianPing.settings import *
import re
import json
from DianPing.items import ShopInfoItem,CommentsItem,EmojiItem
from DianPing.settings import *
from sqlalchemy import create_engine,Column,Integer,String,Table,MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from DianPing.pipelines import ShopInfoTemplate
import jsonpath_rw_ext

class ShopinfoSpider(scrapy.Spider):
    '''
        name : 爬虫名称
        allowed_domains:被允许的域名
        start_request:构造获取店铺下所有评论内容的请求
        get_s_comment:解析店铺初始加载页面中的评论信息
        get_comment:解析从ajax中获取的评论信息
    '''
    name = 'dianping'
    allowed_domains = ['m.dianping.com']

    def start_requests(self):
        #使用sqlalchemy连接mysql数据库，并从shopinfo数据表中提取shopId与reviewCount字段
        engine = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(user=MYSQL_USER,password=MYSQL_PASSWORD,host=MYSQL_HOST,port=MYSQL_PORT,database=MYSQL_DATABASE))
        session = sessionmaker(bind=engine)
        sess = session()
        Base = declarative_base()
        shopinfo = type('shopinfo',(Base,ShopInfoTemplate),{'__tablename__':'shopinfo'})
        ret = sess.query(shopinfo.shopid,shopinfo.reviewcount).all()
        for i in ret:
            shopid = i[0]
            reviewCount = i[1]
            
            #利用从数据库中获取的shopId字段获取店铺评论的初始加载页面，并使用回调函数get_s_comment进行解析.
            yield scrapy.Request('https://m.dianping.com/shop/{shopid}/review_all'.format(shopid=shopid), callback=self.get_s_comment)
            
            #利用从数据库获取的reviewCount字段，按照每个ajax请求获取10条评论的原则，获得获取所有评论需要访问ajax请求的次数.
            page_number = (int(reviewCount) - 6) // 10 + 1

            #构造每次访问ajax请求所需要的data数据
            for index in range(1, page_number + 1):
                    data_comments = {
                        "moduleInfoList": [
                            {
                                "moduleName": "reviewlist",
                                "query": {
                                    "shopId": "{shopid}".format(shopid=shopid),
                                    "offset": index * 10,
                                    "limit": 10,
                                    "type": 1,
                                    "pageDomain": "m.dianping.com"
                                }
                            }
                        ],
                        "pageEnName": "shopreviewlist"
                    }
                    #构造访问ajax数据的post请求，并将结果使用回调函数get_comment进行处理
                    yield scrapy.Request('https://m.dianping.com/isoapi/module', body=json.dumps(data_comments),method='POST',callback=self.get_comment)

    def get_s_comment(self,response):
        #使用正则提取初始加载页面下的评论信息
        pattern_comment = re.compile(
            '.*?"reviewId":(\d+).*?"addTime":"(.*?)".*?"lastTime":"(.*?)".*?"followNoteNo":(\d+)'
            '.*?"browseCount":(\d+)..*?"star":(\d+).*?"reviewBody":"(.*?)","avgPrice":(\d+).*?"userNickName":"(.*?)"'
            '.*?"userPower":(.*?),.*?"contentId":(\d+)'
            , re.S)
        pattern = re.compile('"shopName":"(.*?)".*?"shopId":"(.*?)"', re.S)
        pattern_emoji = re.compile(u'<img class=\\\\"emoji-img\\\\" src=\\\\"(.*?)\\\\" alt=\\\\"\\[(.*?)\\]\\\\">',re.S)
        s_comments = pattern_comment.findall(response.text)
        shopinfo = pattern.findall(response.text)
        for s_comment in s_comments:
            #提取评论内容里的emoji表情，并存入数据库中的emoji表中
            emoji = pattern_emoji.findall(s_comment[6])
            for i in emoji:
                emoji_item = EmojiItem()
                emoji_item['emoji_url'] = i[0]
                emoji_item['emoji_name'] = i[1]
                yield emoji_item

            item = CommentsItem()
            item['shopname'] = shopinfo[0][0]
            item['shopid'] = shopinfo[0][1]
            item['reviewid'] = s_comment[0]
            item['addtime'] = s_comment[1]
            item['lasttime'] = s_comment[2]
            item['follownoteno'] = s_comment[3]
            item['browsecount'] = s_comment[4]
            item['star'] = s_comment[5]
            
            #将评论内容中的emoji表情的url链接替换为emoji表情的对应文字
            result = re.sub(u'<img.*?alt=\\\\"\\[','emoji(',s_comment[6])
            result = re.sub(u'\\]\\\\">',')',result)
            result = re.sub('<br>','',result)
            item['reviewbody'] = result

            item['avgprice'] = s_comment[7]
            item['usernickname'] = s_comment[8]
            item['userpower'] = s_comment[9]
            item['contentid'] = s_comment[10]
            yield item

    def get_comment(self,response):
        #使用jsonpath_rw_ext对获得的数据进行提取
        html = json.loads(response.text)

        shopid = jsonpath_rw_ext.match('$..shopId',html)
        shopname = jsonpath_rw_ext.match('$..shopName',html)
        reviewid = jsonpath_rw_ext.match('$..reviewId',html)
        addtime = jsonpath_rw_ext.match('$..addTime',html)
        lasttime = jsonpath_rw_ext.match('$..lastTime',html)
        follownoteno = jsonpath_rw_ext.match('$..followNoteNo',html)
        browsecount = jsonpath_rw_ext.match('$..browseCount',html)
        star = jsonpath_rw_ext.match('$..star',html)
        reviewbody = jsonpath_rw_ext.match('$..reviewBody',html)
        avgprice = jsonpath_rw_ext.match('$..avgPrice',html)
        usernickname = jsonpath_rw_ext.match('$..userNickName',html)
        userpower = jsonpath_rw_ext.match('$..userPower',html)
        contentid = jsonpath_rw_ext.match('$..contentId',html)

        for i in range(0,len(usernickname)):
            #提取评论内容中的emoji表情url，并存入数据库的emoji表中
            emoji = re.findall('<img class="emoji-img" src="(.*?)" alt="\\[(.*?)\\]">',str(reviewbody[i]))
            for j in emoji:
                emoji_item = EmojiItem()
                emoji_item['emoji_url'] = j[0]
                emoji_item['emoji_name'] = j[1]
                yield emoji_item

            item = CommentsItem()
            item['shopname'] = shopname[0]
            item['shopid'] = shopid[0]
            item['reviewid'] = str(reviewid[i])
            item['addtime'] = addtime[i]
            item['lasttime'] = lasttime[i]
            item['follownoteno'] = str(follownoteno[i])
            item['browsecount'] = str(browsecount[i])
            item['star'] = str(star[i])
            
            #将评论内容中的emoji表情的url链接替换为emoji表情的对应文字
            result = re.sub('<img class="emoji-img" src=".*?" alt="\\[', 'emoji(', str(reviewbody[i]))
            result = re.sub(']">', ')', result)
            result = re.sub('<br>', '', result)
            item['reviewbody'] = result

            item['avgprice'] = str(avgprice[i])
            item['usernickname'] = usernickname[i]
            item['userpower'] = str(userpower[i])
            item['contentid'] = str(contentid[i])
            yield item




    def parse(self, response):
        pass
