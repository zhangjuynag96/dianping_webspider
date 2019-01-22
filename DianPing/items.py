# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class DianpingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ShopInfoItem(scrapy.Item):
    collection = table = 'shopinfo'
    branchname = Field() #店铺所处商场 
    categoryid = Field() #食品类别id
    categoryname = Field() #食品类别
    shopid = Field() #店铺id
    matchtext = Field() #位置及餐饮类别匹配信息
    name = Field() #店铺名称
    pricetext = Field() #人均消费
    recommendreason = Field() #推荐理由
    reviewcount = Field() #评论数量
    shoppower = Field() #店铺总评分(10为1颗星，15为1.5颗星，以此类推50分为满分为5颗星)

class CommentsItem(scrapy.Item):
    collection = table = 'detail'
    shopid = Field() #店铺id
    shopname = Field() #店铺名称
    reviewbody = Field() #评论内容
    usernickname = Field() #评论人昵称
    reviewid = Field() #此条评论的id
    addtime = Field() #评论初次添加时间
    lasttime = Field() #评论最后一次修改时间
    follownoteno = Field() #此条评论盖楼层数
    browsecount = Field() #此条评论被浏览次数
    star = Field() #对店铺的评分
    avgprice = Field() #人均消费
    userpower = Field() #评论人等级的经验值
    contentid = Field() #此条评论的显示id


class EmojiItem(scrapy.Item):
    collection = table = 'emoji'
    emoji_url = Field() #emoji表情图片url
    emoji_name = Field() #emoji表情名称
