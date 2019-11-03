# -*- coding: utf-8 -*-
import json
from os import path
from bs4 import BeautifulSoup as bs

import scrapy
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response


dirpath = path.dirname(__file__)
LUA_SCRIPT = path.abspath(path.join(dirpath, '..', 'lua_scripts\\test.lua'))


class TestSpiderSpider(scrapy.Spider):
    name = 'test_spider'
    allowed_domains = ['foodpanda.ro']
    start_urls = [
        'https://www.foodpanda.ro/restaurant/v1js/hopaa',
        # 'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        # 'https://www.foodpanda.ro/restaurant/v5wn/pizza-adaggio',
        # 'https://www.foodpanda.ro/restaurant/v4yi/big-belly-vendor',
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
        # inspect_response(response, self)
        parse_item = {}
        html = response.data.get('html', None)
        modals = response.data.get('modals', None)

        soup = bs(html, 'html.parser')
        menu_categories = soup.select('div.dish-category-header')
        menu_categories_names = [x.text.strip() for x in menu_categories]
        menu_lists = soup.select('div.dish-category-header + ul.dish-list')
        for i, menu_list in enumerate(menu_lists):
            item_list = []
            parse_item[menu_categories_names[i]] = item_list

            menu_items = menu_list.select('div.dish-card.h-product.menu__item')

            for j, item in enumerate(menu_items):
                item_name = item.text.strip()
                modal = modals.get(str(i+1), {}).get(str(j+1), {}).get('modal_content', None)
                modal_html = bs(modal, 'html.parser') if modal else None
                item_list.append({
                    'name': item_name,
                    'modal': modal_html.text.strip() if modal_html else None,
                })



        # for res in response.data.values():
        #     # Parse String html snapshot
        #     soup = bs(res, 'html.parser')
        #     # Get product name
        #     product_name = soup.select_one('h2.product-name').text.strip()
        #     data[product_name] = {}
        #     # Parse toppings
        #     toppings = soup.find('div', {'class': 'toppings'})
        #     topping_categories = toppings.find_all('div', {'class': 'product-topping-list'})
        #     for category in topping_categories:
        #         category_name = category.select_one('h3 > span').text.strip()
                
        #         items = category.select_one('.js-topping-options').select('.js-topping-option-radio')
        #         parsed_items = []
        #         for item in items:
        #             name = item.select_one('.radio-text')
        #             price = item.select_one('.product-topping-price')
        #             parsed_items.append({
        #                 'name': name.text.strip() if name else None,
        #                 'price': price.text.strip() if price else None
        #             })
        #         data[product_name][category_name] = parsed_items

        yield parse_item