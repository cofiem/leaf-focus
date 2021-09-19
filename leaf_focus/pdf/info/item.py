import csv
import dataclasses
import json
from dataclasses import field, dataclass
from pathlib import Path

from leaf_focus.support.serialise import LeafFocusJsonEncoder


@dataclass
class Item:
    pdf_path: Path
    entries: dict[str, str] = field(default_factory=dict)

    @classmethod
    def save_csv(cls, path: Path, items: list["Item"]):
        """Save info items to a file."""
        if not path:
            raise ValueError("Must provide path.")
        if path.suffix.lower() != ".csv":
            raise ValueError("Must be a csv file.")

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
    def load_csv(cls, path: Path):
        """Load info items from a file."""
        if not path:
            raise ValueError("Must provide path.")
        if path.suffix.lower() != ".csv":
            raise ValueError("Must be a csv file.")

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
                yield Item(pdf_path=Path(pdf_path), entries=entries)

    def save_json(self, path: Path) -> None:
        """Write this info item to a file."""
        if not path:
            raise ValueError("Must provide path.")
        if path.suffix.lower() != ".json":
            raise ValueError("Must be a json file.")

        with open(path, "wt") as f:
            item_dict = dataclasses.asdict(self)
            json.dump(item_dict, f, indent=2, cls=LeafFocusJsonEncoder)

    @classmethod
    def load_json(cls, path: Path) -> "Item":
        """Read an info item from a file."""
        if not path:
            raise ValueError("Must provide path.")
        if path.suffix.lower() != ".json":
            raise ValueError("Must be a json file.")

        with open(path, "rt") as f:
            item_dict = json.load(f)
            return Item(
                pdf_path=Path(item_dict["pdf_path"]),
                entries=item_dict["entries"],
            )
