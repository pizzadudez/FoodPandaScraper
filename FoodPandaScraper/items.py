# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class VendorItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    rating = scrapy.Field()
    address = scrapy.Field()
    coordinates = scrapy.Field()
    delivery_times = scrapy.Field()
    dish_list = scrapy.Field()


class FoodpandascraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass