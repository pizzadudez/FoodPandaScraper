# -*- coding: utf-8 -*-
from os import path
import json
from bs4 import BeautifulSoup as bs
import lxml.html

import scrapy
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response

dirpath = path.dirname(__file__)
TEST_LUA = path.abspath(path.join(dirpath, '..', 'lua_scripts\\test.lua'))

class TestSpiderSpider(scrapy.Spider):
    name = 'test_spider'
    allowed_domains = ['foodpanda.ro']
    start_urls = ['https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania']

    def start_requests(self):
        click_script = open(TEST_LUA, 'r').read()

        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='execute',
                args={ 'lua_source': click_script, 'html': 1 })

    def parse(self, response):
        soup = bs(response.data['2'], 'html.parser')
        
        parent = soup.find('div', {'class': ['product-topping-list', 'required-list']})
        found1 = parent.find('div', {'class': ['js-tooping-item', 'js-topping-option-radio']})
        found = found1.find('span', {'class': 'radio-text'})
        yield {'found': found.text}
        # inspect_response(response, self)
        # text = response.text.xpath('/html')
        # yield { 'text': text }


        # parsed = {}
        # for i, res in enumerate(response.body):
        #     parsed[i] = res
        # yield parsed
        # first_topping = response.xpath('/html/body/div[3]/div/div/div/div[1]/div[4]/div[1]/div/div/div[1]/div[1]/div/span[2]').extract_first()
        # yield { 'first': first_topping }