import csv
import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

from leaf_focus.components.serialise import LeafFocusJsonEncoder


@dataclass
class PdfItem:
    """Information about a downloaded pdf file."""

    name: str
    category: str
    path: str
    url: str
    referrer: str
    last_updated: str

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
                        "name": i.name,
                        "category": i.category,
                        "path": i.path,
                        "url": i.url,
                        "referrer": i.referrer,
                        "last_updated": i.last_updated,
                    }
                )

    @classmethod
    def load(cls, path: Path):
        """Load file items from a file."""
        with open(path, "rt", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield PdfItem(**row)

    def write(self, path: Path) -> None:
        with open(path, "wt") as f:
            item_dict = dataclasses.asdict(self)
            json.dump(item_dict, f, indent=2, cls=LeafFocusJsonEncoder)

    @classmethod
    def read(cls, path: Path) -> "PdfItem":
        with open(path, "rt") as f:
            item_dict = json.load(f)
            return PdfItem(**item_dict)
