import csv
from pathlib import Path
from typing import List

import scrapy
from scrapy import Item


class PdfItem(Item):
    """Information about a downloaded pdf file."""

    name = scrapy.Field()
    category = scrapy.Field()
    path = scrapy.Field()
    url = scrapy.Field()
    referrer = scrapy.Field()
    last_updated = scrapy.Field()

    @classmethod
    def save(cls, path: Path, items: List["PdfItem"]):
        """Save file items to a file."""
        fields = ["category", "last_updated", "name", "path", "referrer", "url"]
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            for i in items:
                writer.writerow(
                    {
                        "name": i["name"],
                        "category": i["category"],
                        "path": i["path"],
                        "url": i["url"],
                        "referrer": i["referrer"],
                        "last_updated": i["last_updated"],
                    }
                )

    @classmethod
    def load(cls, path: Path):
        """Load file items from a file."""
        with open(path, "rt", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield PdfItem(**row)
