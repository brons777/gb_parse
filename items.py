# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParseLes4Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HHItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    requirements = scrapy.Field()
    author_url = scrapy.Field()
    ads_name = scrapy.Field()
    ads_url = scrapy.Field()
    ads_description = scrapy.Field()
    # url = scrapy.Field()
    # title = scrapy.Field()
    # images = scrapy.Field()
    # description = scrapy.Field()
    # author = scrapy.Field()
    # specification = scrapy.Field()
    # price = scrapy.Field()