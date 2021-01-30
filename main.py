from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from lesson_4.gb_parse_les_4.spiders.autoyuola import HHSpider

from dotenv import load_dotenv


if __name__ == '__main__':
    load_dotenv('.env')
    crawler_settings = Settings()
    crawler_settings.setmodule('gb_parse_les_4.settings')
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HHSpider)
    crawler_process.start()


