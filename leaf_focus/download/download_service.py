import json
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class DownloadService:
    """Download and begin processing pdf files."""

    def start(self, items_dir: Path, cache_dir: Path, config_file: Path):
        settings = get_project_settings()

        with open(config_file, "rt") as f:
            config_data = json.load(f)

        settings.set("CUSTOM_START_URLS", config_data["input_urls"])
        settings.set("CUSTOM_ALLOW_DOMAINS", config_data["allowed_domains"])

        feed_file_template = "/items-%(batch_time)s-%(batch_id)05d.csv"
        key = Path(items_dir).as_uri() + feed_file_template

        feeds = {
            key: {
                "format": "csv",
                "batch_item_count": 100,
                "encoding": "utf8",
            }
        }
        settings.set("FEEDS", feeds)
        settings.set("HTTPCACHE_DIR", str(cache_dir))

        # create crawler process
        process = CrawlerProcess(settings)

        # set the spider to use
        process.crawl("pdf")

        # the script will block here until the crawling is finished
        process.start()

        a = 1
