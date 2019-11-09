from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from FoodPandaScraper.settings import DATABASE


DeclarativeBase = declarative_base()

def db_connect():
    return create_engine(URL(**DATABASE))

def create_tables(engine):
    DeclarativeBase.metadata.create_all(engine)


class Vendor(DeclarativeBase):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    url = Column('url', String)
    image = Column('image', String)
    rating = Column('rating', String)
    address = Column('address', String)
    coordinates = Column('coordinates', String)
    delivery_times = Column('delivery_times', String)
    

class Dish(DeclarativeBase):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    category = Column('category', String)
    description = Column('description', String)
    image = Column('image', String)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))

    vendor = relationship("Vendor", back_populates="dishes")

Vendor.dishes = relationship("Dish", order_by=Dish.id, back_populates="vendor")


class Selector(DeclarativeBase):
    __tablename__ = 'selectors'

    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dishes.id'))

    dish = relationship("Dish", back_populates="selectors")

Dish.selectors = relationship("Selector", order_by=Selector.id, back_populates="dish")


class Option(DeclarativeBase):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    price = Column('price', String)
    selector_id = Column(Integer, ForeignKey('selectors.id'))

    selector = relationship("Selector", back_populates="options")

Selector.options = relationship("Option", order_by=Option.id, back_populates="selector")


# class Deals(DeclarativeBase):
#     __tablename__ = "deals"

#     id = Column(Integer, primary_key=True)
#     name = Column('name', String)
#     # title = Column('title', String)
#     # link = Column('link', String, nullable=True)
#     # location = Column('location', String, nullable=True)
#     # original_price = Column('original_price', String, nullable=True)
#     # price = Column('price', String, nullable=True)
#     # end_date = Column('end_date', DateTime, nullable=True)