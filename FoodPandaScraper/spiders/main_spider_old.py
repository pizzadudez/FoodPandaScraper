# -*- coding: utf-8 -*-
import json
from os import path
from bs4 import BeautifulSoup as bs

import scrapy
from scrapy_splash import SplashRequest
# from scrapy.shell import inspect_response


dirpath = path.dirname(__file__)
LUA_SCRIPT = path.abspath(path.join(dirpath, '..', 'lua_scripts\\main.lua'))


class MainSpider(scrapy.Spider):
    name = 'main_spider'
    allowed_domains = ['foodpanda.ro']
    start_urls = [
        # 'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        # 'https://www.foodpanda.ro/restaurant/v5wn/pizza-adaggio',
        'https://www.foodpanda.ro/restaurant/v4yi/big-belly-vendor',
    ]
    lua_script = open(LUA_SCRIPT, 'r').read()

    def start_requests(self):
        for url in self.start_urls:
            args = {
                'lua_source': self.lua_script,
                'timeout': 300,
                'html': 1,
            }
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='execute',
                args=args
            )

    def parse(self, response):
        data = {}
        for res in response.data.values():
            # Parse String html snapshot
            soup = bs(res, 'html.parser')
            # Get product name
            product_name = soup.select_one('h2.product-name').text.strip()
            data[product_name] = {}
            # Parse toppings
            toppings = soup.find('div', {'class': 'toppings'})
            topping_categories = toppings.find_all('div', {'class': 'product-topping-list'})
            for category in topping_categories:
                category_name = category.select_one('h3 > span').text.strip()
                
                items = category.select_one('.js-topping-options').select('.js-topping-option-radio')
                parsed_items = []
                for item in items:
                    name = item.select_one('.radio-text')
                    price = item.select_one('.product-topping-price')
                    parsed_items.append({
                        'name': name.text.strip() if name else None,
                        'price': price.text.strip() if price else None
                    })
                data[product_name][category_name] = parsed_items

        yield data

        # parent = soup.find('div', {'class': ['product-topping-list', 'required-list']})
        # found1 = parent.find('div', {'class': ['js-tooping-item', 'js-topping-option-radio']})
        # found = parent.find_all('span', {'class': 'radio-text'})
        # topping_list = [x.text.strip() for x in found]
        # yield {'found': topping_list}