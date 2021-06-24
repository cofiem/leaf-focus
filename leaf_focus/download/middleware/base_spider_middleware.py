from pathlib import Path

from scrapy.crawler import Crawler


class BaseSpiderMiddleware:
    @classmethod
    def _get_path(cls, crawler: Crawler, key: str):
        settings = crawler.settings
        value = settings.get(key)
        if not value:
            raise ValueError(f"Missing setting '{key}'.")

        path = Path(value)
        if not path.exists():
            raise ValueError(f"Cannot find path from setting '{key}'.")

        return path
