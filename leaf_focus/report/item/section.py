from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

from leaf_focus.report.item.line_group import LineGroupEnum


@dataclass
class Section:
    title: str
    name: LineGroupEnum
    names: list[str]

    @classmethod
    def load(cls, path: Path) -> Iterable["Section"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
        for item in data:
            yield Section(
                title=item.get("title"),
                name=LineGroupEnum.get_by_value(item.get("name")),
                names=item.get("names") or [],
            )
