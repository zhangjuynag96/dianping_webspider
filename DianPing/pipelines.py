# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from DianPing.settings import *
from sqlalchemy import create_engine,Column,Integer,String,Table,MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from DianPing.items import *

class DianpingPipeline(object):
    def process_item(self, item, spider):
        return item


class ShopInfoTemplate():
    '''
        数据库shopinfo表的映射类
    '''
    id = Column(Integer, primary_key=True)
    shopId = Column(String(100))
    branchName = Column(String(100))
    categoryId = Column(Integer)
    categoryName = Column(String(100))
    matchText = Column(String(100))
    name = Column(String(100))
    priceText = Column(String(100))
    recommendReason = Column(String(100))
    reviewCount = Column(Integer)
    shopPower = Column(Integer)

    def __init__(self,**items):
        for key in items:
            if hasattr(self,key):
                setattr(self,key,items[key])

class CommentsTemplate():
    '''
        数据库detail表的映射类
    '''
    id = Column(Integer, primary_key=True)
    shopId = Column(Integer)
    shopName = Column(String(100))
    reviewBody = Column(String(10000))
    userNickName = Column(String(100))
    reviewId = Column(Integer)
    addTime = Column(String(100))
    lastTime = Column(String(100))
    followNoteNo = Column(Integer)
    browseCount = Column(Integer)
    star = Column(Integer)
    avgPrice = Column(Integer)
    userPower = Column(String(100))
    contentId = Column(Integer)

    def __init__(self,**items):
        for key in items:
            if hasattr(self,key):
                setattr(self,key,items[key])

class EmojiTemplate():
    id = Column(Integer, primary_key=True)
    emoji_url = Column(String(100))
    emoji_name = Column(String(100))
    
    def __init__(self,**items):
        for key in items:
            if hasattr(self,key):
                setattr(self,key,items[key])


class SqlAlachemyPipeline(object):
    '''
        __init__:连接mysql数据库，并将数据表与其对应的类连接起来
        process_item:将每个爬虫产生的item，在判断过数据表是否存在后，存入数据表
    '''
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4'.format(user=MYSQL_USER, password=MYSQL_PASSWORD, host=MYSQL_HOST, port=MYSQL_PORT, database=MYSQL_DATABASE))
        self.session=sessionmaker(bind=self.engine)
        self.sess=self.session()
        Base = declarative_base()
        self.shopinfo = type('shopinfo',(Base,ShopInfoTemplate),{'__tablename__':'shopinfo'})
        self.Comment = type('detail',(Base,CommentsTemplate),{'__tablename__':'detail'})
        self.Emoji = type('emoji',(Base,EmojiTemplate),{'__tablename__':'emoji'})

    def process_item(self,item,spider):
        if isinstance(item,ShopInfoItem):
            result = self.sess.query(self.shopinfo).filter_by(shopId=item['shopId']).first()
            if result:
                pass
            else:
                self.sess.add(self.shopinfo(**item))
                self.sess.commit()
            return item

        elif isinstance(item,CommentsItem):
            exist = self.sess.query(self.Comment).filter_by(lastTime=item['lastTime']).first()
            if exist:
                pass
            else:
                self.sess.add(self.Comment(**item))
                self.sess.commit()
            return item
       
        elif isinstance(item,EmojiItem):
            exist2 = self.sess.query(self.Emoji).filter_by(emoji_url=item['emoji_url']).first()
            if exist2:
                pass
            else:
                self.sess.add(self.Emoji(**item))
                self.sess.commit()
            return item

    def close_spider(self, spider):
        self.sess.close()

