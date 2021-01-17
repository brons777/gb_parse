import os
from dotenv import load_dotenv
import requests
from urllib.parse import urljoin
import bs4
import pymongo
import datetime


class MagnitParser:
    def __init__(self, start_url, data_base):
        self.start_url = start_url
        self.database = data_base["gb_parse_12_01_2021"]

    @staticmethod
    def __get_response(url, *args, **kwargs):
        # todo обработать ошибки запросов и статусов тут
        response = requests.get(url, *args, **kwargs)
        return response

    @property
    def data_template(self):
        months = {"января": 1, "февраля": 2, "декабря": 12}
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href")),
            "promo_name": lambda tag: tag.find("div", attrs={"class": "card-sale__header"}).text,
            "product_name": lambda tag: tag.find("div", attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: float(tag.find_next("div", attrs={"class": "label__price_old"}).find("span", attrs={"class": "label__price-integer"}).text + '.' +
                                     tag.find_next("div", attrs={"class": "label__price_old"}).find("span", attrs={"class": "label__price-decimal"}).text),
            "new_price": lambda tag: float(tag.find_next("div", attrs={"class": "label__price_new"}).find("span", attrs={"class": "label__price-integer"}).text + '.' +
                                     tag.find_next("div", attrs={"class": "label__price_old"}).find("span", attrs={"class": "label__price-decimal"}).text),
            "image_url": lambda tag: urljoin(self.start_url, tag.find("picture").find("img").get("data-src")),
            "date_from": lambda tag: datetime.datetime(2021, months.get([line.rstrip() for line in tag.find("div", attrs={"class": "card-sale__date"}).text.split('\n')][1].split()[2]),
                                              int([line.rstrip() for line in tag.find("div", attrs={"class": "card-sale__date"}).text.split('\n')][1].split()[1])),
            "date_to": lambda tag: datetime.datetime(2021, months.get([line.rstrip() for line in tag.find("div", attrs={"class": "card-sale__date"}).text.split('\n')][2].split()[2]),
                                              int([line.rstrip() for line in tag.find("div", attrs={"class": "card-sale__date"}).text.split('\n')][2].split()[1]))
        }

    @staticmethod
    def __get_soup(response):
        return bs4.BeautifulSoup(response.text, "lxml")

    def run(self):
        for product in self.parse(self.start_url):
            self.save(product)

    def validate_product(self, product_data):
        return product_data

    def parse(self, url):
        soup = self.__get_soup(self.__get_response(url))
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_tag in catalog_main.find_all(
            "a", attrs={"class": "card-sale"}, reversive=False
        ):
            yield self.__get_product_data(product_tag)

    def __get_product_data(self, product_tag):
        data = {}
        for key, pattern in self.data_template.items():
            try:
                data[key] = pattern(product_tag)
            except AttributeError:
                continue
        return data

    def save(self, data):
        collection = self.database["magnit_product"]
        collection.insert_one(data)


if __name__ == "__main__":
    load_dotenv('.env')
    data_base = pymongo.MongoClient(os.getenv("DATA_BASE_URL"))
    parser = MagnitParser("https://magnit.ru/promo/?geo=moskva", data_base)
    parser.run()

