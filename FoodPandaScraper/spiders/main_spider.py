# -*- coding: utf-8 -*-
import json
from os import path
from bs4 import BeautifulSoup as bs

import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

from FoodPandaScraper.items import TestItem


dirpath = path.dirname(__file__)
LUA_SCRIPT = path.abspath(path.join(dirpath, '..', 'lua_scripts\\main.lua'))


class MainSpider(scrapy.Spider):
    name = 'main_spider'
    allowed_domains = ['foodpanda.ro']
    start_urls = [
        'https://www.foodpanda.ro/restaurant/v1js/hopaa',
        'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        'https://www.foodpanda.ro/restaurant/v5wn/pizza-adaggio',
        'https://www.foodpanda.ro/restaurant/v4yi/big-belly-vendor',
    ]
    # start_urls = [
    #     'https://www.foodpanda.ro',
    # ]
    lua_script = open(LUA_SCRIPT, 'r').read()
    json = {}

    def start_requests(self):
        """Starts the request chain."""

        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse_vendor,
                endpoint='execute',
                args={
                    'lua_source': self.lua_script,
                    'timeout': 360,
                    'html': 1,
                }
            )

        # for url in self.start_urls:
        #     yield Request(url=url, callback=self.crawl_cities)

    def crawl_cities(self, response):
        """Initiate vendor crawl for all cities."""

        response_html = response.text
        soup = bs(response_html, 'html.parser')
        city_list = soup.select('section.home-cities a.city-tile')
        city_urls = [response.url + x['href'] for x in city_list]

        for city_url in city_urls:
            item = TestItem()
            request = Request(
                url=city_url,
                callback=self.crawl_vendors,
                meta={'parent': city_url}
            )
            yield request

    def crawl_vendors(self, response):
        """Initiate vendor parse for all vendors."""

        response_html = response.text
        soup = bs(response_html, 'html.parser')
        vendor_list = soup.select('div.restaurants-container ul.vendor-list > li > a')
        vendor_urls = [x['href'] for x in vendor_list]
        
        city_url = response.meta['parent']
        yield {'name': vendor_urls[0]}
        # return {'vendor_urls': vendor_urls}

    def parse_vendor(self, response):
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
                info = item.select_one('div.dish-info')
                info_title = info.select_one('h3.dish-name > span')
                info_description = info.select_one('p.dish-description')
                image = item.select_one('div.photo')
                modal = modals.get(str(i+1), {}).get(str(j+1), {}).get('modal_content', None)

                item_list.append({
                    'dish': {
                        'name': info_title.text.strip(),
                        'description': info_description.text.strip() if info_description else None,
                        'image': image.get('data-src', None) if image else None,
                    },
                    'options': self.parse_modal(modal),
                })

        yield parse_item

    def parse_modal(self, modal):
        html = bs(modal, 'html.parser') if modal else None
        if not html: return None
        content = {}
        # Topping Selection
        topping_selections = html.select('.toppings .product-topping-list')
        for selection in topping_selections or []:
            selection_title = selection.select_one('span.product-topping-list-title-text').text.strip()
            options = selection.select('.js-topping-options .js-topping-option-radio')
            parsed_options = []
            for option in options:
                name = option.select_one('span.radio-text')
                price = option.select_one('span.product-topping-price')
                parsed_options.append({
                    'name': name.text.strip(),
                    'price': price.text.strip() if price else None,
                })
            content[selection_title] = parsed_options
        # Variation Selection (rare)
        variation_selections = html.select('.product-variations .product-topping-list.js-variation-selector')
        for selection in variation_selections or []:
            selection_title = selection.select_one('span.product-topping-list-title-text').text.strip()
            options = selection.select('.product-topping-item')
            parsed_options = []
            for option in options:
                name = option.select_one('span.radio-text')
                price = option.select_one('span.product-topping-price')
                parsed_options.append({
                    'name': name.text.strip(),
                    'price': price.text.strip() if price else None,
                })
            content[selection_title] = parsed_options

        return content