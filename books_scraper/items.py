# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class BookItem(scrapy.Item):
    title = Field()
    img = Field()
    author = Field()
    series = Field()
    rating = Field()
    n_rating = Field()
    n_opinions = Field()
    n_readers = Field()   
    genre = Field()
    category = Field()

class CategoryItem(scrapy.Item):
    url = Field()
    genre = Field()
    category = Field()