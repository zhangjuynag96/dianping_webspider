# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from DianPing.settings import *
from sqlalchemy import create_engine,Column,Integer,String,Table,MetaData,DateTime
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
    shop_id = Column(String(100))
    branch_name = Column(String(100))
    category_id = Column(Integer)
    category_name = Column(String(100))
    match_text = Column(String(100))
    name = Column(String(100))
    avg_cost = Column(String(100))
    reason = Column(String(100))
    review_count = Column(Integer)
    shop_mark = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    content_id = Column(Integer)

    def __init__(self,**items):
        for key in items:
            if hasattr(self,key):
                setattr(self,key,items[key])

class CommentsTemplate():
    '''
        数据库detail表的映射类
    '''
    id = Column(Integer, primary_key=True)
    shop_id = Column(Integer)
    shop_name = Column(String(100))
    content = Column(String(10000))
    nick_name = Column(String(100))
    review_id = Column(Integer)
    post_at = Column(String(100))
    modified_at = Column(String(100))
    comment_amounts = Column(Integer)
    browse_count = Column(Integer)
    star = Column(Integer)
    avg_cost = Column(Integer)
    user_xp = Column(String(100))
    show_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    content_id = Column(Integer)

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
            result = self.sess.query(self.shopinfo).filter_by(shop_id=item['shop_id']).first()
            if result:
                pass
            else:
                self.sess.add(self.shopinfo(**item))
                self.sess.commit()
            return item

        elif isinstance(item,CommentsItem):
            exist = self.sess.query(self.Comment).filter_by(modified_at=item['modified_at']).first()
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

