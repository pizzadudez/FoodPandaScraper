# -*- coding: utf-8 -*-
import json
from os import path
from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.http import Request
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

from sqlalchemy.orm import sessionmaker, query
from FoodPandaScraper.models import db_connect, create_tables
from FoodPandaScraper.models import City, Vendor, Dish, Variation, Topping, Option


dirpath = path.dirname(__file__)
LUA_SCRIPT = path.abspath(path.join(dirpath, '..', 'lua_scripts\\main.lua'))


class MainSpider(scrapy.Spider):
    name = 'main_spider'
    script = open(LUA_SCRIPT, 'r').read()
    allowed_domains = ['foodpanda.ro']
    vendor_timeout = 120
    start_urls = [
        'https://www.foodpanda.ro',

        # 'https://www.foodpanda.ro/chain/cw9yi/pizza-hut-delivery',
        # 'https://www.foodpanda.ro/restaurant/v5gi/azima',
        # 'https://www.foodpanda.ro/restaurant/v1js/hopaa',
        # 'https://www.foodpanda.ro/restaurant/v4rj/pizza-transilvania',
        # 'https://www.foodpanda.ro/restaurant/v5wn/pizza-adaggio',
        # 'https://www.foodpanda.ro/restaurant/v4yi/big-belly-vendor',
        # 'https://www.foodpanda.ro/restaurant/v1ok/taboo-doner',
        # 'https://www.foodpanda.ro/chain/cj2cc/pizza-romana',

        # 'https://www.foodpanda.ro/restaurant/v5ek/cedelicii-delivery',
        # 'https://www.foodpanda.ro/restaurant/v0kk/log-out',
        # 'https://www.foodpanda.ro/restaurant/v4pl/bonita',
        # 'https://www.foodpanda.ro/restaurant/v7qc/pizza-napoli-cuptor-cu-lemne',
    ]
    limit = 1 # per city limit of vendors (debugging)

    def start_requests(self):
        """Starts the request chain."""

        self.engine = db_connect()
        create_tables(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        for url in self.start_urls:
            yield Request(url=url, callback=self.crawl_cities)

        # for url in self.start_urls:
        #     yield SplashRequest(
        #         url=url,
        #         callback=self.parse_vendor,
        #         endpoint='execute',
        #         args={
        #             'lua_source': self.script,
        #             'timeout': self.vendor_timeout,
        #             'html': 1,
        #         }
        #     )

    def crawl_cities(self, response):
        """Initiate vendor crawl for all cities."""

        response_html = response.text
        soup = bs(response_html, 'html.parser')
        city_list = soup.select('section.home-cities a.city-tile')
        city_urls = [response.url + x['href'].strip().lower() for x in city_list]

        for city_url in city_urls:
            yield Request(
                url=city_url,
                callback=self.crawl_vendors,
                meta={'start_url': response.url}
            )

    def crawl_vendors(self, response):
        """Initiate vendor parse for all vendors."""

        response_html = response.text
        soup = bs(response_html, 'html.parser')
        city_name = soup.select_one(
                '.hero-section-content .hero-section-text strong').text.strip()
        vendor_list = soup.select('div.restaurants-container ul.vendor-list > li > a')
        vendor_urls = [response.meta['start_url'] + x['href'] for x in vendor_list]
        
        for count, url in enumerate(vendor_urls):
            if count >= (self.limit or 100_000) : break
            yield SplashRequest(
                url=url,
                callback=self.parse_vendor,
                endpoint='execute',
                args={
                    'lua_source': self.script,
                    'timeout': self.vendor_timeout,
                    'html': 1,
                },
                meta={'city_name': city_name}
            )
        
    def parse_vendor(self, response):
        """Parse vendor info, dish list and individual dish selectors."""
        html_string = response.data.get('html', None) # Splash whole page HTML
        topping_selectors = response.data.get('topping_selectors', None) # Splash Modal elements HTML table
        soup = bs(html_string, 'html.parser')
        vendor = {}

        ## Parse Vendor
        vendor_data = json.loads(soup.select_one('div.menu__list-wrapper')
                .get('data-vendor', {}))
        
        vendor['id'] = vendor_data['id']
        vendor['city_id'] = vendor_data['city_id']
        vendor['coordinates'] = f"{vendor_data['latitude']},{vendor_data['longitude']}"
        vendor['url'] = response.url
        description_modal = soup.select_one('div.modal.rich-description div.vendor-info-page')
        vendor['image'] = soup.select_one('div.vendor-header .hero-banner').get('data-src', None)
        info = description_modal.select_one('div.infos')
        vendor['name'] = vendor_data['name']
        vendor['rating'] = vendor_data['rating']
        panel = description_modal.select_one('div.panel div.content')
        vendor['address'] = panel.select_one('p.vendor-location').text.strip()

        ## Parse Dishses
        dish_categories = [x.text.strip() for x in soup.select(
            'div.dish-category-header h2.dish-category-title')]
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
                        'id': x['id'],
                        'name': x['name'],
                        'price': x['price'],
                        'topping_ids': x['topping_ids']
                        } for x in dish_data_object['product_variations']
                        if len(x['topping_ids']) or
                        len(dish_data_object['product_variations']) > 1]   
                name = dish.select_one('h3.dish-name.fn.p-name')
                description = dish.select_one('p.dish-description')
                image = dish.select_one('div.photo')
                price = dish.select_one('span.price.p-price')
                # Append parsed fields
                dish_data['dishes'].append({
                    'id': dish_data_object['id'],
                    'name': name.text.strip() if name else None,
                    'description': description.text.strip() if description else None,
                    'image': image.get('data-src', None) if image else None,
                    'price': price.text.strip() if price else None,
                    'category': dish_categories[list_num],
                    'variations': variations
                })

        yield {
            'city_name': response.meta.get('city_name', None),
            'vendor': vendor,
            'dishes': dish_data['dishes'],
            'dish_categories': dish_data['dish_categories'],
            'topping_selectors': self.parse_topping_selectors(
                topping_selectors, dish_name_hash_map),
        }

    def parse_topping_selectors(self, topping_selectors, hash_map):
        """Parse topping selectors and their options."""

        parsed_selectors = {}
        for topping_id, html in topping_selectors.items():
            soup = bs(html, 'html.parser')
            class_names = soup.select_one('div.topping').attrs['class']

            required = True if 'selection-required' in class_names else False
            checkbox = True if 'topicOptionCheckbox' in class_names else False
            description = soup.select_one('span.product-topping-list-title-text')
            indication = soup.select_one('p.product-topping-list-indication')

            parsed_options = []
            radio_type = 'checkbox' if checkbox else 'radio'
            options = soup.select(f'div.js-topping-option-{radio_type}')
            for option in options:
                name = option.select_one(f'span.{radio_type}-text')
                price = option.select_one('span.product-topping-price')
                parsed_options.append({
                    'name': name.text.strip(),
                    'price': price.text.strip() if price else None,
                })

            parsed_selectors[int(topping_id)] = {
                'required': required,
                'checkbox': checkbox,
                'description': description.text.strip() if description else None,
                'indication': indication.text.strip() if indication else None,
                'options': parsed_options,
            }

        return parsed_selectors  