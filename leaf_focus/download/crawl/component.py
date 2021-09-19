import os
from logging import Logger
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class Component:
    def __init__(self, logger: Logger, feed_dir: Path, cache_dir: Path):
        self._logger = logger
        self._feed_dir = feed_dir
        self._cache_dir = cache_dir

    def run(self, allowed_domains: list[str], urls: list[dict[str, str]]):
        os.environ["SCRAPY_SETTINGS_MODULE"] = "leaf_focus.piece.download.settings"

        settings = get_project_settings()

        settings.set("LEAF_FOCUS_START_URLS", urls)
        settings.set("LEAF_FOCUS_ALLOWED_DOMAINS", allowed_domains)
        settings.set("LEAF_FOCUS_LINK_EXTRACTOR", allowed_domains)

        feed_file_template = "/items-%(batch_time)s-%(batch_id)05d.csv"
        key = self._feed_dir.as_uri() + feed_file_template
        feeds = {
            key: {
                "format": "csv",
                "batch_item_count": 100,
                "encoding": "utf8",
            }
        }
        settings.set("FEEDS", feeds)

        settings.set("HTTPCACHE_DIR", str(self._cache_dir))

        # create crawler process
        process = CrawlerProcess(settings)

        # set the spider to use
        process.crawl("pdf")

        # the script will block here until the crawling is finished
        process.start()
