import os
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from leaf_focus.support.config import Config


class Download:

    command = "download"
    description = "Find and download pdfs."

    def build(self, sub_parser) -> None:
        """Build the command line."""
        pass

    def run(self, parsed_args) -> None:
        """Run using the parsed args."""

        config_file = parsed_args.config_file  # type: Path

        settings = get_project_settings()

        if not config_file:
            raise ValueError("Must provide config file.")
        if not config_file.exists():
            raise ValueError(f"Config file must exist '{config_file}'.")

        config = Config(config_file)

        # the scrapy pipeline component for celery needs to use the celery app
        # the celery app expects to find the config file from an env var 'LEAF_FOCUS_CONFIG_FILE'
        # so, set this env var
        os.environ["LEAF_FOCUS_CONFIG_FILE"] = str(config_file)

        settings.set("LEAF_FOCUS_CONFIG", config)

        settings.set("LEAF_FOCUS_START_URLS", config.pdf_input_urls)
        settings.set("LEAF_FOCUS_ALLOWED_DOMAINS", config.pdf_allowed_domains)
        settings.set("LEAF_FOCUS_LINK_EXTRACTOR", config.pdf_allowed_domains)

        feed_file_template = "/items-%(batch_time)s-%(batch_id)05d.csv"
        key = Path(config.pdf_items_dir).as_uri() + feed_file_template
        feeds = {
            key: {
                "format": "csv",
                "batch_item_count": 100,
                "encoding": "utf8",
            }
        }
        settings.set("FEEDS", feeds)

        settings.set("HTTPCACHE_DIR", str(config.pdf_cache_dir))

        # create crawler process
        process = CrawlerProcess(settings)

        # set the spider to use
        process.crawl("pdf")

        # the script will block here until the crawling is finished
        process.start()
