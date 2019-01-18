# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from scrapy.http import HtmlResponse
from logging import getLogger
import json
import redis
import random
from DianPing.UserAgent import agents
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.cookies import CookiesMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware



class DianpingSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DianpingDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class UserAgentmiddleware(UserAgentMiddleware):
    '''
    agents:所有的User-Agent都存储在UserAgent.py文件的agents列表中，可以向中自行添加UA.
    process_requeset:随机构造header文件，并在每一次访问请求时自动使用header.
    '''
    def process_request(self, request, spider):
        agent = random.choice(agents)
        request.headers["User-Agent"] = agent
        request.headers['Host'] = 'm.dianping.com'
        request.headers['Connection'] = 'keep-alive'
        request.headers['Origin'] = 'https://m.dianping.com'
        request.headers['Content-Type'] = 'application/json'
        request.headers['Accept'] = '*/*'
        request.headers['Referer'] = 'https://m.dianping.com/shop/122901638/review_all'
        request.headers['Accept-Encoding'] = 'gzip, deflate, br'
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'

class Cookiesmiddleware(CookiesMiddleware):
    '''
    分析得出使用的cookies分为5个部分，其中前三个部分为0-9正整数与24个个小写字母的随机组合；第一个部分有13个字符；第二个部分有14个
    字符；第三个部分为7-8个字符；第四个部分为操作系统的编号'100200'为window操作系统，'dc230'为ubuntu操作系统；第五个部分为第一个部分
    的第11个字符在ASCII码表中的下一位，其他位置字符相同.
    process_request:构造随机cookies，并在每一次访问请求时自动使用cookies.
    '''
    def process_request(self, request, spider):
        seed = '1234567890abcdefghijklmnopqrstuvwxyz'
        code_1 = []
        code_2 = []
        code_3 = []
        for i in range(9):
            code_1.append(random.choice(seed))
        code_1 = '1684' + ''.join(code_1)
        for i in range(13):
            code_2.append(random.choice(seed))
        code_2 = '0' + ''.join(code_2)
        for i in range(8):
            code_3.append(random.choice(seed))
        code_3 = ''.join(code_3)
        code = code_1 + '-' + code_2 + '-' + code_3 + '-' + random.choice(('100200', 'dc230')) + '-' + code_1[0:10] + chr(ord(code_1[10]) + 1) + code_1[11:13]
        request.cookies['_lxsdk_cuid'] = '{code}'.format(code=code)
        request.cookies['_lx_utm'] = 'utm_source%3Dgoogle%26utm_medium%3Dorganic'

