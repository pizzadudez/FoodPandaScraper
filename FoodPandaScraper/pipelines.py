# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from sqlalchemy.orm import sessionmaker, query
from FoodPandaScraper.models import db_connect, create_tables
from FoodPandaScraper.models import Vendor, Dish, Variation, Topping, Option

class VendorPipeline(object):
    """Test Pipeline"""
    def __init__(self):
        """Init db conn and sessionmaker, creates deals table."""
        engine = db_connect()
        create_tables(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        session = self.Session()
        if not item.get('vendor', None):
            return item
        try:
            vendor = Vendor(**item['vendor'])
            session.add(vendor)
            vendor_id = session.query(Vendor).filter(Vendor.url == item['vendor']['url']).first().id
            
            topping_objects = []
            for topping_id, topping in item['topping_selectors'].items():
                topping_instance = Topping(
                    id=topping_id,
                    required=topping['required'],
                    checkbox=topping['checkbox'],
                    description=topping['description'],
                    indication=topping['indication']
                )
                for option in topping['options']:
                    option_instance = Option(
                        name=option['name'],
                        price=option['price']
                    )
                    topping_instance.options.append(option_instance)
                topping_objects.append(topping_instance)
            session.add_all(topping_objects)
            session.commit()
            
            dish_objects = []
            for dish in item['dishes']:
                dish_instance = Dish(
                    id=dish['id'],
                    name=dish['name'],
                    description=dish['description'],
                    image=dish['image'],
                    price=dish['price'],
                    category=dish['category'],
                    vendor_id=vendor_id
                )
                for variation in dish['variations']:
                    variation_instance = Variation(
                        id=variation['variation_id']
                    )
                    for topping_id in variation['topping_ids']:
                        topping = session.query(Topping).filter(Topping.id == int(topping_id)).first()
                        variation_instance.toppings.append(topping)

                    dish_instance.variations.append(variation_instance)
                dish_objects.append(dish_instance)
            session.add_all(dish_objects)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return item


class FoodpandascraperPipeline(object):
    def open_spider(self, spider):
        self.file = open('output/scrapped.json', 'w')
        self.file.write("[\n")
    
    def close_spider(self, spider):
        self.file.write("]")
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(
            dict(item),
            indent = 2,
            separators = (',', ': ')
        ) + ",\n"
        self.file.write(line)
        return item
