# -*- coding: utf-8 -*-
import json
from os import path
from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

from FoodPandaScraper.items import VendorItem


dirpath = path.dirname(__file__)
LUA_SCRIPT = path.abspath(path.join(dirpath, '..', 'lua_scripts\\main.lua'))


class MainSpider(scrapy.Spider):
    name = 'main_spider'
    script = open(LUA_SCRIPT, 'r').read()
    allowed_domains = ['foodpanda.ro']
    start_urls = [
        'https://www.foodpanda.ro/restaurant/v5gi/azima',
        # 'https://www.foodpanda.ro/restaurant/v1js/hopaa',
        # 'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        # 'https://www.foodpanda.ro/restaurant/v5wn/pizza-adaggio',
        # 'https://www.foodpanda.ro/restaurant/v4yi/big-belly-vendor',
        # 'https://www.foodpanda.ro/restaurant/v1ok/taboo-doner',
        # 'https://www.foodpanda.ro/chain/cw9yi/pizza-hut-delivery',
    ]
    # start_urls = [
    #     'https://www.foodpanda.ro',
    # ]

    def start_requests(self):
        """Starts the request chain."""
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse_vendor,
                endpoint='execute',
                args={
                    'lua_source': self.script,
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

    def parse_vendor(self, response):
        """Parse vendor info, dish list and individual dish selectors."""
        html_string = response.data.get('html', None) # Splash whole page HTML
        modals = response.data.get('modals', None) # Splash Modal elements HTML table
        soup = bs(html_string, 'html.parser')
        vendor_data = {}

        ## Parse Vendor
        vendor_data['url'] = response.url
        description_modal = soup.select_one('div.modal.rich-description div.vendor-info-page')
        # vendor_data['image'] = 
        info = description_modal.select_one('div.infos')
        vendor_data['name'] = info.select_one('h1.vendor-name').text.strip()
        vendor_data['rating'] = info.select_one('span.rating strong').text.strip()
        panel = description_modal.select_one('div.panel div.content')
        vendor_data['address'] = panel.select_one('p.vendor-location').text.strip()

        ## Parse Dishses
        dish_categories = [x.text.strip() for x in soup.select('div.dish-category-header')]
        dish_name_hash_map = {x: True for x in 
            soup.select('div.dish-card div.dish-info h3.dish-name')}
        dish_data = {'dishes': [], 'dish_categories': dish_categories}
        # Iterate over all dish lists
        dish_lists = soup.select('div.dish-category-header + ul.dish-list')
        for list_num, dish_list in enumerate(dish_lists):
            dishes = dish_list.select('div.dish-card')
            for dish in dishes:
                # Select elements for dish fields
                dish_data_object = json.loads(dish.get('data-object', '{}'))
                variations = [{
                        'variation_id': x['id'],
                        'topping_ids': x['topping_ids']
                    } for x in dish_data_object['product_variations']]
                name = dish.select_one('h3.dish-name.fn.p-name')
                description = dish.select_one('p.dish-description')
                image = dish.select_one('div.photo')
                price = dish.select_one('span.price.p-price')
                # Append parsed fields
                dish_data['dishes'].append({
                    'name': name.text.strip() if name else None,
                    'description': description.text.strip() if description else None,
                    'image': image.get('data-src', None) if image else None,
                    'price': price.text.strip() if price else None,
                    'category': dish_categories[list_num],
                    'variations': variations
                })

        yield {
            'vendor': vendor_data,
            'dishes': dish_data['dishes'],
            'dish_categories': dish_data['dish_categories'],
            'toppings': None,
        }

    def parse_topping_selectors(self, topping_selectors, hash_map):
        # if not topping_selectors: return
        return []

    def parse_modal2(self, modal):
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