from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


@dataclass
class Section:
    title: str
    name: str
    names: list[str]

    @classmethod
    def load(cls, path: Path) -> Iterable["Section"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
        for item in data:
            title = item.get("title")
            name = item.get("name")
            names = item.get("names") or []
            yield Section(title=title, name=name, names=names)
