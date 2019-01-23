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
    branch_name = Field() #店铺所处商场 
    category_id = Field() #食品类别id
    category_name = Field() #食品类别
    shop_id = Field() #店铺id
    match_text = Field() #位置及餐饮类别匹配信息
    name = Field() #店铺名称
    avg_cost = Field() #人均消费
    reason = Field() #推荐理由
    review_count = Field() #评论数量
    shop_mark = Field() #店铺总评分(10为1颗星，15为1.5颗星，以此类推50分为满分为5颗星)
    created_at = Field() #记录创建时间
    updated_at = Field() #记录修改时间
    content_id = Field() #索引

class CommentsItem(scrapy.Item):
    collection = table = 'detail'
    shop_id = Field() #店铺id
    shop_name = Field() #店铺名称
    content = Field() #评论内容
    nick_name = Field() #评论人昵称
    review_id = Field() #此条评论的id
    post_at = Field() #评论初次添加时间
    modified_at = Field() #评论最后一次修改时间
    comment_amounts = Field() #此条评论盖楼层数
    browse_count = Field() #此条评论被浏览次数
    star = Field() #对店铺的评分
    avg_cost = Field() #人均消费
    user_xp = Field() #评论人等级的经验值
    show_id = Field() #此条评论的显示id
    created_at = Field() #记录创建时间
    updated_at = Field() #记录修改时间
    content_id = Field() #索引


class EmojiItem(scrapy.Item):
    collection = table = 'emoji'
    emoji_url = Field() #emoji表情图片url
    emoji_name = Field() #emoji表情名称
