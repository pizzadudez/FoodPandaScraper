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


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    url = Column('url', String)
    image = Column('image', String)
    rating = Column('rating', String)
    address = Column('address', String)
    coordinates = Column('coordinates', String)
    delivery_times = Column('delivery_times', String)
    # Children
    dishes = relationship("Dish", back_populates="vendor")


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
    variations = relationship('Variation', back_populates='dish')


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
    options = relationship('Option', back_populates='topping')


class Option(Base):
    __tablename__ = 'options'
    
    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    price = Column('price', String)
    topping_id = Column(Integer, ForeignKey('toppings.id'))
    # Parent
    topping = relationship('Topping', back_populates='options')


# class Selector(Base):
#     __tablename__ = 'selectors'

#     id = Column(Integer, primary_key=True)
#     dish_id = Column(Integer, ForeignKey('dishes.id'))

#     dish = relationship("Dish", back_populates="selectors")

# Dish.selectors = relationship("Selector", order_by=Selector.id, back_populates="dish")


# class Option(Base):
#     __tablename__ = 'options'

#     id = Column(Integer, primary_key=True)
#     name = Column('name', String)
#     price = Column('price', String)
#     selector_id = Column(Integer, ForeignKey('selectors.id'))

#     selector = relationship("Selector", back_populates="options")

# Selector.options = relationship("Option", order_by=Option.id, back_populates="selector")


# class Deals(Base):
#     __tablename__ = "deals"

#     id = Column(Integer, primary_key=True)
#     name = Column('name', String)
#     # title = Column('title', String)
#     # link = Column('link', String, nullable=True)
#     # location = Column('location', String, nullable=True)
#     # original_price = Column('original_price', String, nullable=True)
#     # price = Column('price', String, nullable=True)
#     # end_date = Column('end_date', DateTime, nullable=True)