from pathlib import Path

from prefect import Task

from leaf_focus.download.crawl.item import Item as DownloadCrawlItem


class DownloadCrawlTask(Task):
    """A Prefect task to collect the spider output."""

    def __init__(self, **kwargs):
        kwargs = {**kwargs, "name": "download.crawl"}
        super().__init__(**kwargs)

    # noinspection PyMethodOverriding
    def run(self, feed_dir: Path) -> list[DownloadCrawlItem]:
        """Run the task."""
        result = []
        for csv_path in feed_dir.glob("*.csv"):
            for item in DownloadCrawlItem.load(csv_path):
                result.append(item)
        return result
