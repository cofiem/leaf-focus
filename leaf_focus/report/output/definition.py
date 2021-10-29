import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable

import yaml


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


@dataclass
class DefinitionTable:
    form_who: list[str]
    form_name: Optional[list[str]]
    form_activity: Optional[list[str]]
    form_participation: Optional[list[str]]
    form_location: Optional[list[str]]

    @classmethod
    def load(cls, items: list[dict]) -> "DefinitionTable":
        raw = {
            "form_who": [],
            "form_name": [],
            "form_activity": [],
            "form_participation": [],
            "form_location": [],
        }
        for item in items:
            for key, value in item.items():
                if value is None:
                    continue

                if isinstance(value, list):
                    raw[key].extend(value)
                else:
                    raw[key].append(value)

        return DefinitionTable(**raw)

    @property
    def column_count(self):
        cols = [
            self.form_who,
            self.form_name,
            self.form_activity,
            self.form_participation,
            self.form_location,
        ]
        items = [i for i in cols if i]
        return len(items)

    @property
    def other_column_name(self):
        """
        For a two-column table, get the name of the column
        that is not the 'who'. column.
        """
        cols = {
            "form_name": self.form_name,
            "form_activity": self.form_activity,
            "form_participation": self.form_participation,
            "form_location": self.form_location,
        }
        for name, value in cols.items():
            if value:
                return name

        raise ValueError()

    def __str__(self):
        raw = {
            "form_who": self.form_who,
            "form_name": self.form_name,
            "form_activity": self.form_activity,
            "form_participation": self.form_participation,
            "form_location": self.form_location,
        }
        return "; ".join(f"{k}={v}" for k, v in raw.items() if v)


@dataclass
class Definition:
    name: str
    lines: Optional[list[DefinitionLine]]
    table: Optional[DefinitionTable]

    @classmethod
    def load(cls, path: Path) -> Iterable["Definition"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
            for item in data:
                lines = item.get("lines")
                table = item.get("table")
                yield Definition(
                    name=item["name"],
                    lines=list(DefinitionLine.load(lines)) if lines else None,
                    table=DefinitionTable.load(table) if table else None,
                )

    def __str__(self):
        def_type = "lines" if self.lines else "table"
        return f"{self.name} ({def_type})"
