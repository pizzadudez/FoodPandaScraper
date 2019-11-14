from FoodPandaScraper.settings import DATABASE

from sqlalchemy import create_engine, Column, Table
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

Base = declarative_base()

def db_connect():
    return create_engine(URL(**DATABASE))

def create_tables(engine):
    Base.metadata.create_all(engine)


class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    # Children
    vendors = relationship('Vendor', back_populates='city', cascade='delete')


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    url = Column('url', String)
    image = Column('image', String)
    rating = Column('rating', String)
    address = Column('address', String)
    coordinates = Column('coordinates', String)
    city_id = Column(Integer, ForeignKey('cities.id'))
    # Parent
    city = relationship('City', back_populates='vendors')
    # Children
    dishes = relationship("Dish", back_populates="vendor", cascade='delete')


class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    description = Column('description', String)
    image = Column('image', String)
    price = Column('price', String)
    category = Column('category', String)
    vendor_id = Column(Integer, ForeignKey('vendors.id'))
    # Parent
    vendor = relationship("Vendor", back_populates="dishes")
    # Children
    variations = relationship('Variation', back_populates='dish', cascade='delete')


variations_toppings = Table('variations_toppings', Base.metadata,
    Column('variation_id', Integer, ForeignKey('variations.id')),
    Column('topping_id', Integer, ForeignKey('toppings.id'))
)   


class Variation(Base):
    __tablename__ = 'variations'
    
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    price = Column('price', String)
    dish_id = Column(Integer, ForeignKey('dishes.id'))
    # Parent
    dish = relationship('Dish', back_populates='variations')
    # Children
    toppings = relationship(
        'Topping',
        secondary=variations_toppings,
        back_populates='variations'
    )


class Topping(Base):
    __tablename__ = 'toppings'

    id = Column(Integer, primary_key=True)
    required = Column('required', Boolean)
    checkbox = Column('checkbox', Boolean)
    description = Column('description', String)
    indication = Column('indication', String)
    # Parents
    variations = relationship(
        'Variation',
        secondary=variations_toppings,
        back_populates='toppings'    
    )
    # Children
    options = relationship('Option', back_populates='topping', passive_deletes=True)


class Option(Base):
    __tablename__ = 'options'
    
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    price = Column('price', String)
    topping_id = Column(Integer, ForeignKey('toppings.id', ondelete="cascade"))
    # Parent
    topping = relationship('Topping', back_populates='options')