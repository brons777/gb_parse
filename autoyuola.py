import scrapy
import pymongo
import os
import re
import builtins
from urllib.parse import urljoin
from lesson_4.gb_parse_les_4.loaders import HHLoader

class HHSpider(scrapy.Spider):

    # data_base = pymongo.MongoClient(os.getenv("DATA_BASE_URL"))
    # database = data_base["gb_parse_12_01_2021_les_4"]

    name = 'headhunter'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    css_query = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'ads': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href',
    }

    data_main_xpath = {
        'name': "//div[@class='vacancy-serp-item__info']//a[@target='_blank']/text()",
        'salary': "//div[@class='vacancy-serp-item__sidebar']/span[@data-qa='vacancy-serp__vacancy-compensation']/text()",
        'description': "//div[@data-qa='vacancy-serp__vacancy_snippet_responsibility']/text()",
        'requirements': "//div[@data-qa='vacancy-serp__vacancy_snippet_requirement']/text()",
        'author_url': "//div[@class='vacancy-serp-item__sidebar']/a/@href",
    }

    data_xpath = {
        'ads_name': '//h1/span[contains(@class, "company-header-title-name")]/text()',
        'ads_url': '//a[contains(@data-qa, "company-site")]/@href',
        'ads_description': '//div[contains(@data-qa, "company-description")]//text()',
    }


    def parse(self, response):
        for link in response.xpath(self.css_query['pagination']):
            yield response.follow(link, callback=self.parse)

        for vacancy in response.xpath(self.css_query['ads']):
            yield response.follow(vacancy, callback=self.ads_parse)


    def ads_parse(self, response):
        loader1 = HHLoader(response=response)
        for key, value in self.data_main_xpath.items():
            loader1.add_xpath(key, value)
        yield loader1.load_item()
        yield response.follow(response.xpath(self.data_main_xpath['author_url']).get(), callback=self.comp_parse)


    def comp_parse(self, response, **kwargs):
        loader2 = HHLoader(response=response)
        for key, value in self.data_xpath.items():
            loader2.add_xpath(key, value)
        yield loader2.load_item()
        # yield response.follow(response.xpath(self.data_main_xpath['author_url']).get(), callback=self.comp_parse_2)

    # def comp_parse_2(self, response):
    #     for ids in range(10):
    #         yield {'item': ids}


