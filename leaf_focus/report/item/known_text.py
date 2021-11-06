from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


@dataclass
class KnownText:
    category: str
    names: list[str]

    @classmethod
    def load(cls, path: Path) -> Iterable["KnownText"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
        for item in data:
            yield KnownText(names=item.get("names"), category=item.get("category"))
