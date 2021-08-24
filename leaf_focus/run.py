import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from leaf_focus.report.report_service import ReportService
from leaf_focus.support.config import Config


class Run:

    _activity_download = "download"
    _activity_report = "report"

    def __init__(self):
        self._logger = None

    def from_args(self, args: Namespace):
        name = args.sub_parser_name

        # scrapy has an internal logger
        if name != "download":
            self._create_logger()

        if name == self._activity_download:
            self.download(args.config_file)
        elif name == self._activity_report:
            self.report(args.config_file)
        else:
            raise ValueError(f"Unrecognised activity '{name}'.")

    def download(self, config_file: Path):
        """Find and download pdf files."""

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

    def report(self, config_file: Path):
        self._log_start(self._activity_report)
        report = ReportService(self._logger)
        # report.start(items_dir, cache_dir, output_dir)
        self._log_end(self._activity_report)

    def _create_logger(self):
        logging.basicConfig(
            format="%(asctime)s - %(levelname)-8s - %(name)s: %(message)s",
            level=logging.INFO,
        )
        self._logger = logging.getLogger("leaf-focus")

    def _log_start(self, name: str):
        if self._logger:
            self._logger.info(f"Starting {name}.")

    def _log_end(self, name: str):
        if self._logger:
            self._logger.info(f"Finished {name}.")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Extract text from pdf files.",
    )
    parser.add_argument(
        "--config-file",
        type=Path,
        help="Path to the config file.",
    )
    subparsers = parser.add_subparsers(
        dest="sub_parser_name",
        help="Available commands.",
    )

    # create the parser for the "download" command
    sub_parser_download = subparsers.add_parser(
        "download",
        help="Find and download pdfs.",
    )

    # create the parser for the "report" command
    sub_parser_report = subparsers.add_parser(
        "report",
        help="Recognise text from each line of each pdf page.",
    )
    sub_parser_report.add_argument(
        "--output-dir",
        type=Path,
        help="Path to directory to save the report files.",
    )

    parsed_args = parser.parse_args()
    if parsed_args.sub_parser_name:
        Run().from_args(parsed_args)
    else:
        parser.print_help()
