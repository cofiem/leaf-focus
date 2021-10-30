import re
from dataclasses import dataclass
from typing import Iterable


@dataclass
class DefinitionLine:
    values: list[str]
    regex: bool

    @classmethod
    def load(cls, items: list[dict]) -> Iterable["DefinitionLine"]:
        for item in items:
            value = item.get("value")
            values = item.get("values")
            regex = item.get("regex") or False
            if not values and value:
                values = [value]
            yield DefinitionLine(values=values, regex=regex)

    @property
    def regexes(self):
        if self.regex:
            return [re.compile(i) for i in self.values]
        return None

    def __str__(self):
        return ", ".join(f"'{i}'" for i in self.values)
