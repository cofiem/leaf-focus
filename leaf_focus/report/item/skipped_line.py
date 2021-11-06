import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SkippedLine:
    """Details of a line that was not matched by any parser."""

    count: int
    text: str

    @classmethod
    def save(cls, path: Path, items: Iterable["SkippedLine"]):
        """Save items to a csv file."""
        fields = ["count", "text"]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields, dialect="excel")
            writer.writeheader()
            for i in items:
                writer.writerow({"count": i.count, "text": i.text})

    def __str__(self):
        items = [
            ("count", self.count),
            ("text", self.text),
        ]
        return "; ".join(f"{k}={v}" for k, v in items if v)
