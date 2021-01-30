import re
from urllib.parse import urljoin

from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import HHItem


def clear_unicode(value):
    return value.replace('\u202f', "")


def in_float(value):
    try:
        return float(value)
    except ValueError:
        return None

# def get_author_url(item):
#     author_url = []
#     for i in range(len(item)):
#         base_url = 'https://hh.ru'
#         result = urljoin(base_url, item[i])
#         author_url.append(result)
#     return author_url


class HHLoader(ItemLoader):
    default_item_class = HHItem
    # name_in = get_name
    name_out = TakeFirst()
    salary_in = MapCompose(clear_unicode, in_float)
    salary_out = TakeFirst()
    description_in = "".join
    description_out = TakeFirst()
    requirements_out = TakeFirst()
    author_url_out = TakeFirst()
    ads_name_out = TakeFirst()
    ads_url_out = TakeFirst()
    ads_description_out = TakeFirst()



    # url_out = TakeFirst()
    # title_out = TakeFirst()
    # price_in = MapCompose(clear_unicode, in_float)
    # price_out = TakeFirst()
    # author_in = MapCompose(get_author_id, get_author_url)
    # author_out = TakeFirst()
    # specifications_in = MapCompose(get_specification)
    # specifications_out = specifications_output