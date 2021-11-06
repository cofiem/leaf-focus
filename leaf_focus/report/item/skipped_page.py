import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class SkippedPage:
    """Details of a page that was not seen."""

    pdf_path: Path
    pdf_hash_type: str
    pdf_hash_value: str
    pdf_page: str
    pdf_url: str

    @classmethod
    def save(cls, path: Path, items: Iterable["SkippedPage"]):
        """Save items to a csv file."""
        fields = [
            "pdf_page",
            "pdf_url",
            "pdf_hash_type",
            "pdf_hash_value",
            "pdf_path",
        ]
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields, dialect="excel")
            writer.writeheader()
            for i in items:
                writer.writerow(
                    {
                        "pdf_page": i.pdf_page,
                        "pdf_url": i.pdf_url,
                        "pdf_hash_type": i.pdf_hash_type,
                        "pdf_hash_value": i.pdf_hash_value,
                        "pdf_path": i.pdf_path,
                    }
                )

    def __str__(self):
        items = [
            ("pdf_page", self.pdf_page),
            ("pdf_url", self.pdf_url),
            ("pdf_hash_type", self.pdf_hash_type),
            ("pdf_hash_value", self.pdf_hash_value),
            ("pdf_path", self.pdf_path),
        ]
        return "; ".join(f"{k}={v}" for k, v in items if v)
