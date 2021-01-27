import scrapy
import pymongo
import os
import re
from urllib.parse import urljoin

class AutoyuolaSpider(scrapy.Spider):

    data_base = pymongo.MongoClient(os.getenv("DATA_BASE_URL"))
    database = data_base["gb_parse_12_01_2021_les_4"]

    name = 'autoyuola'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']
    css_query = {
        'brands': 'div.TransportMainFilters_brandsList__2tIkv div.ColumnItemList_container__5gTrc a.blackLink',
        'pagination': 'div.Paginator_block__2XAPy a.Paginator_button_u1e7D',
        'ads': 'div.SerpSnippet_titleWrapper__38bZM a.blackLink',
    }

    data_query = {
        'title': lambda q: q.css('div.AdvertCard_advertTitle__1S1Ak::text').get(),
        'price': lambda q: q.css('div.AdvertCard_price__3dDCr::text').get(),
        'description': lambda q: q.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
        "year": lambda q: q.css('div.AdvertSpecs_row__ljPcX a.blackLink::text').extract()[0],
        "mileage": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[0],
        "body": lambda q: q.css('div.AdvertSpecs_data__xK2Qx a.blackLink::text').extract()[1],
        "transmission": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[1],
        "engine": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[2],
        "color": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[4],
        "drive": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[5],
        "power": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[6],
        "VIN": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[7],
        "customs cleared": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[8],
        "owners": lambda q: q.css('div.AdvertSpecs_data__xK2Qx::text').extract()[9],
        "photos": lambda q: q.css('img').extract()[1:],
        "user_url": lambda q: urljoin('auto.youla.ru/user/', re.split('youlaId%22%2C%22([a-zA-Z | \d]+)%22%2C%22avatar', q.css('script').extract()[-6])[1]),
        # "phone": ' '


    }

    @staticmethod
    def gen_tasks(response, link_list, callback):
        for link in link_list:
            yield  response.follow(link.attrib.get('href'), callback= callback)

    def parse(self, response):
        yield from self.gen_tasks(response, response.css(self.css_query['brands']), self.brand_parse)


    def brand_parse(self, response):
        yield from self.gen_tasks(response, response.css(self.css_query['pagination']), self.brand_parse)
        yield from self.gen_tasks(response, response.css(self.css_query['ads']), self.ads_parse)

    def ads_parse(self, response):
        data = {}
        count = 0
        ind = 0
        for key, query in self.data_query.items():
            try:
                data[key] = query(response)
            except (ValueError, AttributeError):
                continue
            # count += 1
            # if count in [5, 7, 8, 9, 10, 11, 12, 13]:
            #     ind += 1
            # data[key] = response.css(query).extract()[ind]
            # if count == 13:
            #     ind = 0
        self.save(data)

    def save(self, data):
        collection = self.database["auto_product"]
        collection.insert_one(data)

