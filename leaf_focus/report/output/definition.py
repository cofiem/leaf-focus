from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable

import yaml

from leaf_focus.report.output.definition_alteration_table import (
    DefinitionAlterationTable,
)
from leaf_focus.report.output.definition_line import DefinitionLine
from leaf_focus.report.output.definition_section_table import DefinitionSectionTable


@dataclass
class Definition:
    name: str
    lines: Optional[list[DefinitionLine]]
    section_table: Optional[DefinitionSectionTable]
    alteration_table: Optional[DefinitionAlterationTable]

    @classmethod
    def load(cls, path: Path) -> Iterable["Definition"]:
        with open(path, "rt", encoding="utf8") as f:
            data = yaml.safe_load(f)
            for item in data:
                lines = item.get("lines")
                if lines:
                    def_lines = list(DefinitionLine.load(lines))
                else:
                    def_lines = None

                sec_table = item.get("section_table")
                if sec_table:
                    def_sec_table = DefinitionSectionTable.load(sec_table)
                else:
                    def_sec_table = None

                alt_table = item.get("alteration_table")
                if alt_table:
                    def_alt_table = DefinitionAlterationTable.load(alt_table)
                else:
                    def_alt_table = None

                yield Definition(
                    name=item["name"],
                    lines=def_lines,
                    section_table=def_sec_table,
                    alteration_table=def_alt_table,
                )

    def __str__(self):
        if self.lines:
            def_type = "lines"
        elif self.section_table:
            def_type = "section_table"
        elif self.alteration_table:
            def_type = "alteration_table"
        else:
            raise ValueError()
        return f"{self.name} ({def_type})"
