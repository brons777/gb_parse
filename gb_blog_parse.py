import os
import requests
import bs4
import database
from dotenv import load_dotenv
from urllib.parse import urljoin
import datetime
import time
import json

class ParseError(Exception):
    def __init__(self, txt):
        self.txt = txt


class GbParse:
    params = {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36",
        "Accept-Language": "ru,en;q=0.9",
    }
    flag: bool

    def __init__(self, start_url, db):
        self.db = db
        self.start_url = start_url
        self.done_url = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parse)]
        self.done_url.add(self.start_url)

    @staticmethod
    def _get_response(*args, **kwargs):
        # TODO обработки ошибок
        return requests.get(*args, **kwargs)

    def _get_soup(self, *args, **kwargs):
        response = self._get_response(*args, **kwargs)
        return bs4.BeautifulSoup(response.text, "lxml")

    def parse_task(self, url, callback):
        def wrap():
            soup = self._get_soup(url)
            return callback(url, soup)

        return wrap

    def run(self):
        for task in self.tasks:
            result = task()
            if result:
                self.save(result)

    def pag_parse(self, url, soup):
        for a_tag in soup.find("ul", attrs={"class": "gb__pagination"}).find_all("a"):
            pag_url = urljoin(url, a_tag.get("href"))
            if pag_url not in self.done_url:
                task = self.parse_task(pag_url, self.pag_parse)
                self.tasks.append(task)
            self.done_url.add(pag_url)
        for a_post in soup.find("div", attrs={"class": "post-items-wrapper"}).find_all(
                "a", attrs={"class": "post-item__title"}
        ):
            post_url = urljoin(url, a_post.get("href"))
            if post_url not in self.done_url:
                task = self.parse_task(post_url, self.post_parse)
                self.tasks.append(task)
            self.done_url.add(post_url)



    def post_parse(self, url, soup):
        self.flag = False
        title = soup.find("h1", attrs={"class": "blogpost-title"}).text
        author_name_tag = soup.find("div", attrs={"itemprop": "author"})
        first_image_url = soup.find('img').get('src')
        date_post = datetime.date(int(soup.find("time").get('datetime')[:4]),
                                  int(soup.find("time").get('datetime')[5:7]),
                                  int(soup.find("time").get('datetime')[8:10]))
        params = self.params
        params["commentable_type"] = soup.find("div", attrs={"class": "referrals-social-buttons-small-wrapper"}).get(
            "data-minifiable-type")
        params["commentable_id"] = soup.find("div", attrs={"class": "referrals-social-buttons-small-wrapper"}).get(
            "data-minifiable-id")
        try:
            response_comment = self._get_response("https://geekbrains.ru/api/v2/comments", headers=self.headers,
                                                  params=params)
            if response_comment.status_code > 399:
                raise ParseError(response_comment.status_code)
        except (requests.RequestException, ParseError):
            time.sleep(0.5)
        comment_content = json.loads(response_comment.text)
        data =  {
                "data_post":
                    {
                        "url": url,
                        "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
                        "date_post": date_post,
                    },
                "author": {
                    "url": urljoin(url, author_name_tag.parent.get("href")),
                    "name": author_name_tag.text,
                },
                "tags": [
                    {"name": tag.text,
                     "url": urljoin(url, tag.get("href"))}
                    for tag in soup.find("article").find_all("a", attrs={"class": "small"})
                ],
                "comments": {},
        }
        if comment_content:
            result_data= {}
            for ind, comment in enumerate(comment_content, 1):
                data["comments"] = {}
                data["comments"] = {
                    "comment_author": comment["comment"]["user"].get("full_name"),
                    "comment_text":comment["comment"].get("body")
                },
                result_data[ind] = data.copy()
            return result_data
        self.flag = True
        return data


    def save(self, data: dict):
        if self.flag:
            self.db.create_post(data)
        else:
            for key, item in data.items():
                item['comments'] = item['comments'][0]
                self.db.create_post(item)


if __name__ == "__main__":
    load_dotenv('.env')
    parser = GbParse("https://geekbrains.ru/posts", database.Database(os.getenv("SQLDB_URL")))
    parser.run()
