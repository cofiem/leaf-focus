import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


@dataclass
class LineParser:
    value: str
    is_regex: bool
    group: str
    line_type: str

    def __post_init__(self):
        if self.is_regex:
            self.regex = re.compile(self.value)
        else:
            self.regex = None

    @classmethod
    def load(cls, path: Path) -> Iterable["LineParser"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
        for item in data:
            yield LineParser(
                value=item.get("value"),
                is_regex=item.get("regex"),
                group=item.get("group"),
                line_type=item.get("type"),
            )

    def collapse_spaces(self, value: str) -> str:
        return re.sub(r"\s+", " ", value)

    def match(self, value: str) -> tuple[bool, dict]:
        if self.is_regex:
            match = self.regex.match(value)
            is_match = match is not None
            if is_match:
                extracted = dict(
                    (k, {"value": v, "span": match.span(k)})
                    for k, v in match.groupdict().items()
                )
            else:
                extracted = {}
        else:
            value_norm = self.collapse_spaces(value).strip()
            is_match = value_norm == self.value
            extracted = {}

        return is_match, extracted

    def __str__(self):
        return f"{self.line_type}:{self.group} '{self.value}'"
