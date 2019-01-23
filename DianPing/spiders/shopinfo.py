# -*- coding: utf-8 -*-
import scrapy
import requests
from DianPing.settings import *
import re
import json
from DianPing.items import ShopInfoItem,CommentsItem
import jsonpath_rw_ext
import datetime

class ShopinfoSpider(scrapy.Spider):
    '''
        name:爬虫名称
        allowed_domains:被允许的域名
        headers:request请求需要的头文件
        cookies:request请求需要的cookies
        start_request:构造获取店铺内容的scrapy.request与scrapy.post请求
        get_s_shopinfo:解析scrapy.request请求获取到的初始加载页面的店铺信息
        get_shopinfo:解析scrapy.post请求获取到的店铺信息
    '''
    name = 'shopinfo'
    allowed_domains = ['m.dianping.com']

    headers = {
        'Host': 'm.dianping.com',
        'Connection': 'keep-alive',
        'Origin': 'https://m.dianping.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Referer': 'https://m.dianping.com/shop/122901638/review_all',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    cookies = {
        '_lxsdk_cuid': '1684b9f6a1ac8-0947303a1ed79d-74266752-dc230-1684b9f6a1ac8',
        '_lx_utm': 'utm_source%3Dgoogle%26utm_medium%3Dorganic',
    }

    def start_requests(self):
        #访问初始页面，获取美食频道下店铺的总数量和初始加载页面所加载出来的店铺的数量.其中type为按什么排序方式获取，o1d1为距离优先,o2d1为人气优先,o3d1为好评优先.
        type = 'o2d1'
        s_shop_list = requests.get('https://m.dianping.com/nanjing/ch10/{type}'.format(type=type), cookies=self.cookies, headers=self.headers)
        pattern_getshopcount = re.compile('{"count":(\d+),"distance":0,"favIcon":"","id":10,"name":"美食","parentId":0,"sortId":0}')
        shop_counts = pattern_getshopcount.findall(s_shop_list.text)
        pattern_shopinfo = re.compile('"branchName":"(.*?)","categoryId":(\d+),"categoryName":"(.*?)"'
                                      '.*?"id":"(.*?)"'
                                      '.*?"matchText":"(.*?)","name":"(.*?)"'
                                      '.*?"priceText":"(.*?)".*?"recommendReason":"(.*?)"'
                                      '.*?"reviewCount":(\d+).*?"shopPower":(\d+)'
                                        , re.S)
        s_shopinfo = pattern_shopinfo.findall(s_shop_list.text)
 
        #获得初始页面直接加载出来的店铺数量
        s_shop_num = 0
        for s_shop in s_shopinfo:
            s_shop_num += 1
        
        #生成初始页面请求,并交予回调函数get_s_shopinfo处理,分析初始加载页面直接加载出来的店铺的信息
        yield scrapy.Request('https://m.dianping.com/nanjing/ch10/{type}'.format(type=type), callback=self.get_s_shopinfo)
        print(shop_counts)
        #将获取到的美食频道下的店铺总数量减去初始加载页面直接加载出来的店铺数量，并按照访问一次ajax数据可获得20家店铺信息的原则，构造出总共需要访问ajax数据的次数.
        count = (int(shop_counts[0]) - s_shop_num) // 20
        
        #构造每一次ajax请求所需要的data数据
        for page in range(1, count + 2):
            for cityId in range(1,2506):
                data_shoplist = {
                    "pageEnName": "shopList",
                    "moduleInfoList": [
                        {
                            "moduleName": "mapiSearch",
                            "query": {
                                "search": {
                                    "start": page * 20,
                                    "categoryId": "10",
                                    "parentCategoryId": 10,
                                    "locateCityid": 0,
                                    "limit": 20,
                                    "sortId": "2",
                                    "cityId": cityId,
                                    "range": "-1",
                                    "maptype": 0,
                                    "keyword": ""
                                }
                            }
                        }
                    ]
                }
                #构造post请求，获得ajax数据，并交予回调函数get_shopinfo进行处理
                yield scrapy.Request('https://m.dianping.com/isoapi/module', body=json.dumps(data_shoplist),method='POST',callback=self.get_shopinfo)

    def get_s_shopinfo(self,response):
        #使用正则对数据进行提取
        pattern_shopinfo = re.compile('"branchName":"(.*?)","categoryId":(\d+),"categoryName":"(.*?)"'
                                      '.*?"id":"(.*?)","matchText":"(.*?)","name":"(.*?)"'
                                      '.*?"priceText":"(.*?)".*?"recommendReasonData":{(.*?)},"regionName"'
                                      '.*?"reviewCount":(\d+).*?"shopPower":(\d+)'
                                      , re.S)
        s_shopinfo = pattern_shopinfo.findall(response.text)
        for s_shop in s_shopinfo:
            item = ShopInfoItem()
            item['branch_name'] = s_shop[0]
            item['category_id'] = s_shop[1]
            item['category_name'] = s_shop[2]
            item['shop_id'] = s_shop[3]
            item['match_text'] = s_shop[4]
            item['name'] = s_shop[5]
            item['avg_cost'] = s_shop[6]
            
            #解决部分店铺没有recommendReason字段的问题
            recommendReason = re.sub('"iconHeight":0,"iconWidth":0,"recommendReason":"', '', s_shop[7])
            recommendReason = re.sub('","recommendReasonType":0,"recommendReasonUserId":0', '', recommendReason)
            item['reason'] = recommendReason
            
            item['review_count'] = s_shop[8]
            item['shop_mark'] = s_shop[9]
            item['created_at'] = datetime.datetime.now()
            item['updated_at'] = datetime.datetime.now()
            item['content_id'] = 0
            yield item

    def get_shopinfo(self,response):
        #使用jsonpath_rw_ext对数据进行提取
        html = json.loads(response.text)
        
        branchName = jsonpath_rw_ext.match('$..branchName',html)
        categoryId = jsonpath_rw_ext.match('$..categoryId',html)
        categoryName = jsonpath_rw_ext.match('$..categoryName',html)
        id = jsonpath_rw_ext.match('$..id',html)
        matchText = jsonpath_rw_ext.match('$..matchText',html)
        name = jsonpath_rw_ext.match('$..name',html)
        priceText = jsonpath_rw_ext.match('$..priceText',html)
        recommendReasonData = jsonpath_rw_ext.match('$..recommendReasonData',html)
        reviewCount = jsonpath_rw_ext.match('$..reviewCount',html)
        shopPower = jsonpath_rw_ext.match('$..shopPower',html)
        
        for i in range(0,len(name)):
            item = ShopInfoItem()
            item['branch_name'] = branchName[i]
            item['category_id'] = str(categoryId[i])
            item['category_name'] = categoryName[i]
            item['shop_id'] = id[i]
            item['match_text'] = matchText[i]
            item['name'] = name[i]
            item['avg_cost'] = priceText[i]

            #解决部分店铺没有recommendReason字段的问题
            recommendReason = re.sub("{'iconHeight': 0, 'iconWidth': 0,", '', str(recommendReasonData[i]))
            recommendReason = re.sub("'recommendReasonType': 0, 'recommendReasonUserId': 0}", '', recommendReason)
            recommendReason = re.sub("'recommendReason': '", '', recommendReason)
            recommendReason = re.sub("',",'',recommendReason)
            item['reason'] = recommendReason
            
            item['review_count'] = str(reviewCount[i])
            item['shop_mark'] = str(shopPower[i])
            item['created_at'] = datetime.datetime.now()
            item['updated_at'] = datetime.datetime.now()
            item['content_id'] = 0
            yield item



    def parse(self, response):
        pass
