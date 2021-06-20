from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class DownloadService:
    def start(self):
        process = CrawlerProcess(get_project_settings())

        process.crawl("pdf")

        # the script will block here until the crawling is finished
        process.start()
