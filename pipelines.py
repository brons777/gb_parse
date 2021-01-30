# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import os

class GbParseLes4Pipeline:
    def process_item(self, item, spider):
        return item


class SaveToMongo:
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv("DATA_BASE_URL"))
        self.db = self.client["gb_parse_12_01_2021_les_5"]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item