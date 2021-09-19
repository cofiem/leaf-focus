import csv
import dataclasses
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from leaf_focus.support.serialise import LeafFocusJsonEncoder, LeafFocusJsonDecoder


@dataclass
class Item:
    """Identify a pdf file using the path and hash."""

    pdf_file: Path
    hash_type: str
    file_hash: str

    @classmethod
    def save(cls, path: Path, items: Iterable["Item"]) -> None:
        """Save file items to a file."""
        fields = ["pdf_file", "hash_type", "file_hash"]
        with open(path, "wt", newline="", encoding="utf8") as f:
            writer = csv.DictWriter(f, fields)
            writer.writeheader()
            for i in items:
                writer.writerow(
                    {
                        "pdf_file": str(i.pdf_file),
                        "hash_type": i.hash_type,
                        "file_hash": i.file_hash,
                    }
                )

    @classmethod
    def load(cls, path: Path) -> Iterable["Item"]:
        """Load file items from a file."""
        with open(path, "rt", encoding="utf8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield Item(
                    pdf_file=Path(row["pdf_file"]),
                    hash_type=row["hash_type"],
                    file_hash=row["file_hash"],
                )

    def write(self, path: Path) -> None:
        with open(path, "wt") as f:
            item_dict = dataclasses.asdict(self)
            json.dump(item_dict, f, indent=2, cls=LeafFocusJsonEncoder)

    @classmethod
    def read(cls, path: Path) -> "Item":
        with open(path, "rt") as f:
            item_dict = json.load(f, cls=LeafFocusJsonDecoder)
            return Item(
                pdf_file=Path(item_dict["pdf_file"]),
                hash_type=item_dict["hash_type"],
                file_hash=item_dict["file_hash"],
            )
