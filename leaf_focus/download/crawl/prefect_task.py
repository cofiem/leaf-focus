from pathlib import Path

from prefect import Task

from leaf_focus.download.crawl.item import Item as DownloadCrawlItem


class PrefectTask(Task):
    """A Prefect task to collect the spider output."""

    # noinspection PyMethodOverriding
    def run(self, feed_dir: Path) -> DownloadCrawlItem:
        """Run the task."""
        for csv_path in feed_dir.glob("*.csv"):
            for item in DownloadCrawlItem.load(csv_path):
                yield item
