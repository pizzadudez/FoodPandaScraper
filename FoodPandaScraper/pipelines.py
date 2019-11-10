# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
from sqlalchemy.orm import sessionmaker, query
from FoodPandaScraper.models import db_connect, create_tables
from FoodPandaScraper.models import Vendor, Dish, Selector, Option

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
            dish_objects = []
            for dish in item['dishes']:
                dish_instance = Dish(
                    name=dish['name'],
                    description=dish['description'],
                    image=dish['image'],
                    price=dish['price'],
                    category=dish['category'],
                    vendor_id=vendor_id
                )
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
