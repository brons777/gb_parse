import json
import time
from pathlib import Path
import requests

class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt


class Parse5ka:
    params = {
        "records_per_page": 50,
        "page": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36",
        "Accept-Language": "ru,en;q=0.9",
    }


    def __init__(self, start_url, result_path):
        self.start_url = start_url
        self.result_path = result_path

    @staticmethod
    def __get_response(url, *args, **kwargs) -> requests.Response:
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue

    def run(self):
        response_categories = self.__get_response("https://5ka.ru/api/v2/categories", headers=self.headers)
        self.data_product = json.loads(response_categories.text)
        self.parse(self.start_url)


    def parse(self, url):
        for categories in self.data_product:
            products = []
            url = self.start_url
            params = self.params
            params['categories'] = categories['parent_group_code']
            while url:
                response = self.__get_response(url, headers=self.headers, params=params)
                if params:
                    params = {}
                data = json.loads(response.text)
                products += data.get("results")
                url = data.get("next")
            path = self.result_path.joinpath(f"{categories['parent_group_name']}.json")
            product = {"name": categories['parent_group_name'], "code": categories['parent_group_code'], "products": products}
            self.save(product, path)

    @staticmethod
    def save(data, path: Path):
        with path.open("w", encoding="UTF-8") as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == "__main__":
    result_path = Path(__file__).parent.joinpath("products")
    url = "https://5ka.ru/api/v2/special_offers/"
    # parser = Parse5ka(url, result_path)
    parser = Parse5ka(url, result_path)
    parser.run()
