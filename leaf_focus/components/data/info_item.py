import csv
import dataclasses
import json
from dataclasses import field, dataclass
from pathlib import Path

from leaf_focus.components.serialise import LeafFocusJsonEncoder


@dataclass
class InfoItem:
    pdf_path: Path
    entries: dict[str, str] = field(default_factory=dict)

    @classmethod
    def save(cls, path: Path, items: list["InfoItem"]):
        """Save file items to a file."""
        fields = ["pdf_path", "key", "value"]
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            for i in items:
                for k, v in i.entries.items():
                    writer.writerow(
                        {"pdf_path": str(i.pdf_path), "key": str(k), "value": str(v)}
                    )

    @classmethod
    def load(cls, path: Path):
        """Load file items from a file."""
        with open(path, "rt", encoding="utf8") as f:
            reader = csv.DictReader(f)

            items = {}
            for row in reader:
                pdf_path = row.get("pdf_path")
                key = row.get("key")
                value = row.get("value")
                if pdf_path not in items:
                    items[pdf_path] = {}
                items[pdf_path][key] = value

            for pdf_path, entries in items.items():
                yield InfoItem(pdf_path=pdf_path, entries=entries)

    def write(self, path: Path) -> None:
        with open(path, "wt") as f:
            item_dict = dataclasses.asdict(self)
            json.dump(item_dict, f, indent=2, cls=LeafFocusJsonEncoder)

    @classmethod
    def read(cls, path: Path) -> "InfoItem":
        with open(path, "rt") as f:
            item_dict = json.load(f)
            return InfoItem(**item_dict)
