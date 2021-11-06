import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


@dataclass
class Correction:
    find: str
    replace: str
    is_regex: bool
    category: str

    def __post_init__(self):
        if self.is_regex:
            self.regex = re.compile(self.find)
        else:
            self.regex = re.compile(r"\b" + re.escape(self.find) + r"\b")

    @classmethod
    def load(cls, path: Path) -> Iterable["Correction"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
        for item in data:
            yield Correction(
                find=item.get("find"),
                replace=item.get("replace"),
                is_regex=item.get("regex") or False,
                category=item.get("category"),
            )
